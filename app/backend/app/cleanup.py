from pathlib import Path

from . import config
from .models import TaskStatus
from .task_store import expire_if_needed, iter_tasks


def expire_done_tasks() -> int:
    changed = 0
    for record in iter_tasks():
        updated = expire_if_needed(record)
        if updated.status != record.status:
            changed += 1
    return changed


def cleanup_expired_files() -> int:
    removed = 0
    for record in iter_tasks():
        updated = expire_if_needed(record)
        if updated.status != TaskStatus.EXPIRED:
            continue
        paths = [updated.video_path, updated.audio_path]
        paths.extend(variant.audio_path for variant in updated.audio_variants.values())
        for maybe_path in paths:
            if maybe_path and _remove_relative_path(maybe_path):
                removed += 1
    return removed


def _remove_relative_path(relative_path: str) -> bool:
    path = (config.BASE_DIR / relative_path).resolve()
    data_root = config.DATA_DIR.resolve()
    if data_root not in path.parents and path != data_root:
        return False
    if path.exists() and path.is_file():
        path.unlink()
        return True
    return False
