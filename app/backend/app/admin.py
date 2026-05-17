from __future__ import annotations

import shutil
import re
from collections import Counter

from . import config
from .models import TaskRecord
from .task_store import iter_tasks


def admin_status() -> dict:
    config.ensure_data_dirs()
    tasks = iter_tasks()
    counts = Counter(record.status.value for record in tasks)
    data_usage = shutil.disk_usage(config.DATA_DIR)

    return {
        "backend": {
            "status": "ok",
            "version": config.APP_VERSION,
            "processing_mode": "mock" if config.MOCK_PROCESSING else "real",
        },
        "sidecar": {
            "status": "configured" if config.SIDECAR_BASE_URL else "missing",
        },
        "storage": {
            "data_total_bytes": data_usage.total,
            "data_used_bytes": data_usage.used,
            "data_free_bytes": data_usage.free,
            "videos_count": count_files(config.VIDEOS_DIR),
            "audio_count": count_files(config.AUDIO_DIR),
            "tasks_count": count_files(config.TASKS_DIR),
        },
        "tasks": {
            "counts": dict(counts),
            "recent": [task_summary(record) for record in recent_tasks(tasks, 20)],
        },
    }


def admin_tasks() -> dict:
    tasks = iter_tasks()
    return {
        "tasks": [task_summary(record) for record in recent_tasks(tasks, 20)],
    }


def recent_tasks(tasks: list[TaskRecord], limit: int) -> list[TaskRecord]:
    return sorted(tasks, key=lambda record: record.created_at, reverse=True)[:limit]


def task_summary(record: TaskRecord) -> dict:
    pitch_jobs = list(record.pitch_jobs.values())
    return {
        "task_id": record.task_id,
        "status": record.status.value,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "expires_at": record.expires_at,
        "share_text_preview": redact_urls(record.share_text_preview),
        "audio_url": record.audio_url,
        "variants_count": max(len(record.audio_variants) - 1, 0),
        "pitch_jobs_count": len(pitch_jobs),
        "pitch_failed_count": sum(1 for job in pitch_jobs if job.status == "failed"),
        "error_code": record.error_code.value if record.error_code else None,
    }


def count_files(path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file())


def redact_urls(value: str) -> str:
    return re.sub(r"https?://\S+", "[link]", value or "")
