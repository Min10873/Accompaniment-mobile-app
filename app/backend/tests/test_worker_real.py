from app import config
from app.models import ErrorCode, TaskStatus
from app.task_store import create_task
from app.worker import process_task_real


def test_process_task_real_uses_download_and_extract_boundaries(monkeypatch):
    calls = []

    def fake_download(_douyin_url, target_path):
        calls.append("download")
        target_path.write_bytes(b"mp4")
        return target_path

    def fake_extract(_video_path, target_path):
        calls.append("extract")
        target_path.write_bytes(b"mp3")
        return target_path

    monkeypatch.setattr("app.worker.download_video", fake_download)
    monkeypatch.setattr("app.worker.extract_mp3", fake_extract)
    record = create_task("real", "https://v.douyin.com/real123/")

    updated = process_task_real(record)

    assert calls == ["download", "extract"]
    assert updated.status == TaskStatus.DONE
    assert updated.video_path is None
    assert updated.audio_url is not None
    assert updated.audio_url.startswith("/files/audio/")
    assert updated.audio_path is not None
    assert (config.BASE_DIR / updated.audio_path).exists()


def test_process_task_real_marks_download_failure(monkeypatch):
    def fake_download(_douyin_url, _target_path):
        raise RuntimeError(ErrorCode.DOWNLOAD_FAILED.value)

    monkeypatch.setattr("app.worker.download_video", fake_download)
    record = create_task("download fail", "https://v.douyin.com/fail123/")

    updated = process_task_real(record)

    assert updated.status == TaskStatus.FAILED
    assert updated.error_code == ErrorCode.DOWNLOAD_FAILED


def test_process_task_real_marks_extract_failure(monkeypatch):
    def fake_download(_douyin_url, target_path):
        target_path.write_bytes(b"mp4")
        return target_path

    def fake_extract(_video_path, _target_path):
        raise RuntimeError(ErrorCode.EXTRACT_FAILED.value)

    monkeypatch.setattr("app.worker.download_video", fake_download)
    monkeypatch.setattr("app.worker.extract_mp3", fake_extract)
    record = create_task("extract fail", "https://v.douyin.com/fail123/")

    updated = process_task_real(record)

    assert updated.status == TaskStatus.FAILED
    assert updated.error_code == ErrorCode.EXTRACT_FAILED
