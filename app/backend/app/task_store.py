from __future__ import annotations

import json
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path

from . import config
from .models import (
    AudioVariant,
    ErrorCode,
    PitchCreateRequest,
    PitchJobRecord,
    PitchJobStatus,
    StageTimestamps,
    TaskRecord,
    TaskStatus,
)


ACTIVE_STATUSES = {
    TaskStatus.QUEUED,
    TaskStatus.DOWNLOADING,
    TaskStatus.EXTRACTING,
}
ACTIVE_PITCH_STATUSES = {
    PitchJobStatus.QUEUED,
    PitchJobStatus.PROCESSING,
}


def utc_now() -> datetime:
    return datetime.now().astimezone()


def iso_now() -> str:
    return utc_now().isoformat(timespec="seconds")


def make_task_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(config.TASK_ID_LENGTH))


def make_pitch_job_id() -> str:
    return make_task_id()


def task_path(task_id: str) -> Path:
    return config.TASKS_DIR / f"{task_id}.json"


def preview_share_text(share_text: str) -> str:
    collapsed = " ".join((share_text or "").split())
    return collapsed[: config.SHARE_TEXT_PREVIEW_LIMIT]


def load_task(task_id: str) -> TaskRecord | None:
    path = task_path(task_id)
    if not path.exists():
        return None
    return TaskRecord.model_validate_json(path.read_text(encoding="utf-8"))


def save_task(record: TaskRecord) -> None:
    config.ensure_data_dirs()
    path = task_path(record.task_id)
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(
        json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def iter_tasks() -> list[TaskRecord]:
    config.ensure_data_dirs()
    records: list[TaskRecord] = []
    for path in sorted(config.TASKS_DIR.glob("*.json")):
        records.append(TaskRecord.model_validate_json(path.read_text(encoding="utf-8")))
    return records


def has_active_task() -> bool:
    now = utc_now()
    for record in iter_tasks():
        record = expire_if_needed(record, now)
        if record.status in ACTIVE_STATUSES:
            return True
        if any(job.status in ACTIVE_PITCH_STATUSES for job in record.pitch_jobs.values()):
            return True
    return False


def create_task(share_text: str, douyin_url: str) -> TaskRecord:
    config.ensure_data_dirs()
    now = utc_now()
    task_id = make_task_id()
    while task_path(task_id).exists():
        task_id = make_task_id()

    created = now.isoformat(timespec="seconds")
    expires = (now + timedelta(days=config.RETENTION_DAYS)).isoformat(timespec="seconds")
    record = TaskRecord(
        task_id=task_id,
        status=TaskStatus.QUEUED,
        created_at=created,
        updated_at=created,
        expires_at=expires,
        share_text_preview=preview_share_text(share_text),
        douyin_url=douyin_url,
        stage_timestamps=StageTimestamps(queued_at=created),
    )
    save_task(record)
    return record


def update_task(record: TaskRecord, **changes: object) -> TaskRecord:
    data = record.model_dump()
    data.update(changes)
    data["updated_at"] = iso_now()
    updated = TaskRecord.model_validate(data)
    save_task(updated)
    return updated


def variant_key(direction: str, semitones: int) -> str:
    return f"{direction}_{semitones}"


def label_for_variant(direction: str, semitones: int) -> str:
    label = "升调" if direction == "up" else "降调"
    return f"{label} {semitones} 个半音"


def ensure_original_variant(record: TaskRecord) -> TaskRecord:
    if "original" in record.audio_variants or not record.audio_path or not record.audio_url:
        return record
    variant = AudioVariant(
        kind="original",
        audio_path=record.audio_path,
        audio_url=record.audio_url,
        created_at=record.stage_timestamps.done_at or record.updated_at,
        expires_at=record.expires_at,
        source=None,
        label="原调",
    )
    variants = dict(record.audio_variants)
    variants["original"] = variant
    return update_task(record, audio_variants=variants)


def cached_variant(record: TaskRecord, key: str) -> AudioVariant | None:
    variant = record.audio_variants.get(key)
    if variant is None:
        return None
    path = config.BASE_DIR / variant.audio_path
    if path.exists() and path.stat().st_size > 0:
        return variant
    return None


def create_pitch_job(record: TaskRecord, request: PitchCreateRequest) -> tuple[TaskRecord, PitchJobRecord]:
    now = iso_now()
    job_id = make_pitch_job_id()
    while job_id in record.pitch_jobs:
        job_id = make_pitch_job_id()

    key = variant_key(request.direction.value, request.semitones)
    job = PitchJobRecord(
        pitch_job_id=job_id,
        status=PitchJobStatus.QUEUED,
        variant_key=key,
        direction=request.direction,
        semitones=request.semitones,
        created_at=now,
        updated_at=now,
    )
    jobs = dict(record.pitch_jobs)
    jobs[job_id] = job
    updated = update_task(record, pitch_jobs=jobs)
    return updated, job


def update_pitch_job(
    record: TaskRecord,
    job: PitchJobRecord,
    **changes: object,
) -> tuple[TaskRecord, PitchJobRecord]:
    data = job.model_dump()
    data.update(changes)
    data["updated_at"] = iso_now()
    updated_job = PitchJobRecord.model_validate(data)
    jobs = dict(record.pitch_jobs)
    jobs[job.pitch_job_id] = updated_job
    updated_record = update_task(record, pitch_jobs=jobs)
    return updated_record, updated_job


def add_pitch_variant(record: TaskRecord, job: PitchJobRecord, audio_path: str, audio_url: str) -> TaskRecord:
    created = iso_now()
    variant = AudioVariant(
        kind="pitch",
        direction=job.direction,
        semitones=job.semitones,
        audio_path=audio_path,
        audio_url=audio_url,
        created_at=created,
        expires_at=record.expires_at,
        source="original",
        label=label_for_variant(job.direction.value, job.semitones),
    )
    variants = dict(record.audio_variants)
    variants[job.variant_key] = variant
    return update_task(record, audio_variants=variants)


def create_uploaded_task(
    *,
    audio_path: str,
    audio_url: str,
    source: str,
    label: str = "原调",
) -> TaskRecord:
    config.ensure_data_dirs()
    now = utc_now()
    task_id = make_task_id()
    while task_path(task_id).exists():
        task_id = make_task_id()

    created = now.isoformat(timespec="seconds")
    expires = (now + timedelta(days=config.RETENTION_DAYS)).isoformat(timespec="seconds")
    variant = AudioVariant(
        kind="original",
        audio_path=audio_path,
        audio_url=audio_url,
        created_at=created,
        expires_at=expires,
        source=source,
        label=label,
    )
    record = TaskRecord(
        task_id=task_id,
        status=TaskStatus.DONE,
        created_at=created,
        updated_at=created,
        expires_at=expires,
        share_text_preview="",
        douyin_url="",
        audio_path=audio_path,
        audio_url=audio_url,
        audio_variants={"original": variant},
        stage_timestamps=StageTimestamps(queued_at=created, done_at=created),
    )
    save_task(record)
    return record


def expire_if_needed(record: TaskRecord, now: datetime | None = None) -> TaskRecord:
    now = now or utc_now()
    if record.is_expired_at(now):
        return update_task(
            record,
            status=TaskStatus.EXPIRED,
            audio_url=None,
            error_code=ErrorCode.TASK_EXPIRED,
        )
    return record
