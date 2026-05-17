from datetime import timedelta

from app import config
from app.cleanup import cleanup_expired_files
from app.models import AudioVariant, ErrorCode, PitchDirection, TaskStatus
from app.task_store import create_task, load_task, update_task, utc_now


def test_cleanup_expired_files_removes_expired_audio_and_video():
    record = create_task("done", "https://v.douyin.com/done123/")
    audio_path = config.AUDIO_DIR / "old.mp3"
    pitch_path = config.AUDIO_DIR / "old-up-3.mp3"
    video_path = config.VIDEOS_DIR / f"{record.task_id}.mp4"
    audio_path.write_bytes(b"mp3")
    pitch_path.write_bytes(b"pitch")
    video_path.write_bytes(b"mp4")
    update_task(
        record,
        status=TaskStatus.DONE,
        audio_path=str(audio_path.relative_to(config.BASE_DIR)),
        audio_url="/files/audio/old.mp3",
        audio_variants={
            "up_3": AudioVariant(
                kind="pitch",
                direction=PitchDirection.UP,
                semitones=3,
                audio_path=str(pitch_path.relative_to(config.BASE_DIR)),
                audio_url="/files/audio/old-up-3.mp3",
                created_at=utc_now().isoformat(timespec="seconds"),
                source="original",
                label="升调 3 个半音",
            )
        },
        video_path=str(video_path.relative_to(config.BASE_DIR)),
        expires_at=(utc_now() - timedelta(seconds=1)).isoformat(timespec="seconds"),
    )

    removed = cleanup_expired_files()
    updated = load_task(record.task_id)

    assert removed == 3
    assert updated is not None
    assert updated.status == TaskStatus.EXPIRED
    assert updated.error_code == ErrorCode.TASK_EXPIRED
    assert not audio_path.exists()
    assert not pitch_path.exists()
    assert not video_path.exists()
