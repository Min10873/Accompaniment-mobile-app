from datetime import timedelta

from app.models import ErrorCode, TaskStatus
from app.task_store import create_task, has_active_task, load_task, preview_share_text, task_path, update_task
from app.task_store import utc_now


def test_create_task_saves_preview_without_full_share_text():
    share_text = "抖音分享文本 " + "很长" * 100 + " https://v.douyin.com/abc123/"

    record = create_task(share_text, "https://v.douyin.com/abc123/")

    assert record.status == TaskStatus.QUEUED
    assert record.share_text_preview == preview_share_text(share_text)
    assert len(record.share_text_preview) <= 80
    assert record.share_text_preview != share_text


def test_has_active_task_checks_only_non_terminal_statuses():
    active = create_task("a", "https://v.douyin.com/abc123/")
    assert has_active_task() is True

    update_task(active, status=TaskStatus.DONE)
    assert has_active_task() is False


def test_expired_done_task_is_not_active():
    record = create_task("a", "https://v.douyin.com/abc123/")
    update_task(
        record,
        status=TaskStatus.DONE,
        expires_at=(utc_now() - timedelta(seconds=1)).isoformat(timespec="seconds"),
    )

    assert has_active_task() is False


def test_update_task_persists_expected_fields():
    record = create_task("a", "https://v.douyin.com/abc123/")
    updated = update_task(
        record,
        status=TaskStatus.FAILED,
        error_code=ErrorCode.DOWNLOAD_FAILED,
        error_detail="local only",
    )

    assert updated.status == TaskStatus.FAILED
    assert updated.error_code == ErrorCode.DOWNLOAD_FAILED
    assert updated.error_detail == "local only"


def test_old_task_json_without_pitch_fields_still_loads():
    path = task_path("OLDTASK1")
    path.write_text(
        """
{
  "task_id": "OLDTASK1",
  "status": "done",
  "created_at": "2026-05-04T00:00:00+08:00",
  "updated_at": "2026-05-04T00:00:00+08:00",
  "expires_at": "2026-05-11T00:00:00+08:00",
  "share_text_preview": "old",
  "douyin_url": "https://v.douyin.com/old123/",
  "video_path": null,
  "audio_path": "data/audio/old.mp3",
  "audio_url": "/files/audio/old.mp3",
  "error_code": null,
  "error_detail": null,
  "stage_timestamps": {
    "queued_at": "2026-05-04T00:00:00+08:00",
    "downloading_at": null,
    "extracting_at": null,
    "done_at": "2026-05-04T00:00:00+08:00",
    "failed_at": null
  }
}
""",
        encoding="utf-8",
    )

    record = load_task("OLDTASK1")

    assert record is not None
    assert record.audio_variants == {}
    assert record.pitch_jobs == {}
