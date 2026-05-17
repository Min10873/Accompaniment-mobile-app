import re
import base64
from datetime import timedelta

from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.models import ErrorCode, TaskStatus
from app.task_store import create_task, load_task, update_task, utc_now
from app.worker import process_task_mock


client = TestClient(app)


def admin_auth_headers(username="admin", password="secret"):
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_health_reports_processing_mode():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": config.APP_VERSION,
        "processing_mode": "mock",
    }


def test_create_task_returns_201_queued_and_creates_task_file():
    response = client.post(
        "/api/tasks",
        json={"share_text": "复制打开抖音 https://v.douyin.com/VUkeE3kU-o8/"},
    )

    assert response.status_code == 201
    body = response.json()
    assert re.fullmatch(r"[A-Z0-9]{8}", body["task_id"])
    assert body["status"] == "queued"
    assert body["audio_url"] is None
    assert body["error_code"] is None

    record = load_task(body["task_id"])
    assert record is not None
    assert record.share_text_preview
    assert record.status == TaskStatus.DONE
    assert record.audio_url is not None


def test_mock_worker_moves_task_to_done_and_sets_audio_url():
    record = create_task("mock", "https://v.douyin.com/mock123/")

    updated = process_task_mock(record)

    assert updated.status == TaskStatus.DONE
    assert updated.audio_url is not None
    assert updated.audio_url.startswith("/files/audio/")
    assert updated.audio_path is not None
    assert updated.audio_path.endswith(".mp3")


def test_create_task_without_douyin_url_returns_422_without_task():
    response = client.post("/api/tasks", json={"share_text": "这里没有链接"})

    assert response.status_code == 422
    body = response.json()
    assert body["task_id"] is None
    assert body["status"] is None
    assert body["error_code"] == ErrorCode.NO_DOUYIN_URL


def test_create_task_when_active_returns_503_without_task():
    create_task("active", "https://v.douyin.com/active123/")

    response = client.post(
        "/api/tasks",
        json={"share_text": "复制打开抖音 https://v.douyin.com/new123/"},
    )

    assert response.status_code == 503
    body = response.json()
    assert body["task_id"] is None
    assert body["status"] is None
    assert body["error_code"] == ErrorCode.SERVER_BUSY


def test_get_task_not_found_returns_404():
    response = client.get("/api/tasks/NOEXIST1")

    assert response.status_code == 404
    body = response.json()
    assert body["status"] is None
    assert body["error_code"] == ErrorCode.TASK_NOT_FOUND


def test_get_failed_task_returns_http_200():
    record = create_task("failed", "https://v.douyin.com/fail123/")
    update_task(record, status=TaskStatus.FAILED, error_code=ErrorCode.DOWNLOAD_FAILED)

    response = client.get(f"/api/tasks/{record.task_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["error_code"] == ErrorCode.DOWNLOAD_FAILED


def test_get_expired_task_returns_http_200():
    record = create_task("done", "https://v.douyin.com/done123/")
    update_task(
        record,
        status=TaskStatus.DONE,
        expires_at=(utc_now() - timedelta(seconds=1)).isoformat(timespec="seconds"),
    )

    response = client.get(f"/api/tasks/{record.task_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "expired"
    assert body["error_code"] == ErrorCode.TASK_EXPIRED


def test_audio_file_mount_returns_404_for_missing_file():
    response = client.get("/files/audio/missing.mp3")

    assert response.status_code == 404


def test_audio_file_mount_returns_200_for_mock_audio():
    record = create_task("mock audio", "https://v.douyin.com/audio123/")
    updated = process_task_mock(record)

    assert updated.audio_url is not None
    response = client.get(updated.audio_url)

    assert response.status_code == 200
    assert response.content


def test_create_pitch_job_and_query_done_result():
    record = create_task("mock audio", "https://v.douyin.com/audio123/")
    original = process_task_mock(record)

    response = client.post(
        f"/api/tasks/{original.task_id}/pitch",
        json={"direction": "up", "semitones": 3},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["pitch_job_id"]
    assert body["status"] == "queued"
    assert body["variant_key"] == "up_3"
    assert body["cached"] is False

    job_response = client.get(f"/api/tasks/{original.task_id}/pitch/{body['pitch_job_id']}")
    assert job_response.status_code == 200
    job_body = job_response.json()
    assert job_body["status"] == "done"
    assert job_body["audio_url"].startswith("/files/audio/")

    updated = load_task(original.task_id)
    assert updated is not None
    assert updated.status == TaskStatus.DONE
    assert updated.audio_url == original.audio_url
    assert "original" in updated.audio_variants
    assert "up_3" in updated.audio_variants


def test_create_pitch_returns_cached_variant_without_new_job():
    record = create_task("mock audio", "https://v.douyin.com/audio123/")
    original = process_task_mock(record)

    first = client.post(
        f"/api/tasks/{original.task_id}/pitch",
        json={"direction": "down", "semitones": 2},
    )
    assert first.status_code == 202
    first_job_id = first.json()["pitch_job_id"]

    second = client.post(
        f"/api/tasks/{original.task_id}/pitch",
        json={"direction": "down", "semitones": 2},
    )

    assert second.status_code == 200
    body = second.json()
    assert body["cached"] is True
    assert body["pitch_job_id"] is None
    assert body["variant_key"] == "down_2"

    updated = load_task(original.task_id)
    assert updated is not None
    assert list(updated.pitch_jobs) == [first_job_id]


def test_pitch_requires_done_source_task():
    record = create_task("queued", "https://v.douyin.com/audio123/")

    response = client.post(
        f"/api/tasks/{record.task_id}/pitch",
        json={"direction": "up", "semitones": 1},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["error_code"] == ErrorCode.SOURCE_NOT_READY


def test_pitch_invalid_semitones_returns_422():
    record = create_task("mock audio", "https://v.douyin.com/audio123/")
    original = process_task_mock(record)

    response = client.post(
        f"/api/tasks/{original.task_id}/pitch",
        json={"direction": "up", "semitones": 12},
    )

    assert response.status_code == 422


def test_pitch_failure_does_not_change_original_done_task(monkeypatch):
    record = create_task("mock audio", "https://v.douyin.com/audio123/")
    original = process_task_mock(record)
    monkeypatch.setattr(config, "MOCK_PROCESSING", False)

    def fail_pitch(_source_path, _target_path, _direction, _semitones):
        raise RuntimeError(ErrorCode.PITCH_FAILED.value)

    monkeypatch.setattr("app.worker.pitch_shift_mp3", fail_pitch)

    response = client.post(
        f"/api/tasks/{original.task_id}/pitch",
        json={"direction": "up", "semitones": 4},
    )

    assert response.status_code == 202
    job_response = client.get(f"/api/tasks/{original.task_id}/pitch/{response.json()['pitch_job_id']}")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "failed"
    assert job_response.json()["error_code"] == ErrorCode.PITCH_FAILED

    updated = load_task(original.task_id)
    assert updated is not None
    assert updated.status == TaskStatus.DONE
    assert updated.audio_url == original.audio_url


def test_api_responses_do_not_expose_sensitive_internals():
    response = client.post(
        "/api/tasks",
        json={"share_text": "复制打开抖音 https://v.douyin.com/VUkeE3kU-o8/"},
    )

    body = response.json()
    serialized = str(body)

    assert "Cookie" not in serialized
    assert "127.0.0.1:8000" not in serialized
    assert "ffmpeg" not in serialized.lower()
    assert "traceback" not in serialized.lower()


def test_admin_status_requires_basic_auth(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "secret")

    response = client.get("/api/admin/status")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="Accompaniment Admin"'


def test_admin_static_page_requires_basic_auth(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "secret")

    response = client.get("/admin/")

    assert response.status_code == 401


def test_admin_routes_are_not_open_when_credentials_are_missing(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "")

    response = client.get("/api/admin/status")

    assert response.status_code == 503
    assert response.headers["www-authenticate"] == 'Basic realm="Accompaniment Admin"'


def test_admin_status_returns_readonly_summary_without_full_task_details(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "secret")
    record = create_task(
        "复制打开抖音 https://v.douyin.com/admin123/ 这是完整分享文本",
        "https://v.douyin.com/admin123/",
    )
    update_task(record, status=TaskStatus.FAILED, error_detail="internal traceback")

    response = client.get("/api/admin/status", headers=admin_auth_headers())

    assert response.status_code == 200
    body = response.json()
    serialized = str(body)
    assert body["backend"]["status"] == "ok"
    assert body["backend"]["version"] == config.APP_VERSION
    assert body["sidecar"]["status"] == "configured"
    assert "data_dir" not in body["storage"]
    assert "tasks" in body
    assert "recent" in body["tasks"]
    assert "https://v.douyin.com/admin123/" not in serialized
    assert "internal traceback" not in serialized
    assert "127.0.0.1:8000" not in serialized
    assert "/data" not in serialized
    assert "/data/" not in serialized
    assert "Cookie" not in serialized


def test_admin_tasks_returns_latest_20_with_auth(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "secret")
    for index in range(25):
        create_task(f"task {index}", f"https://v.douyin.com/admin{index}/")

    response = client.get("/api/admin/tasks", headers=admin_auth_headers())

    assert response.status_code == 200
    assert len(response.json()["tasks"]) == 20


def test_admin_static_page_is_served_with_basic_auth(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "secret")

    response = client.get("/admin/", headers=admin_auth_headers())

    assert response.status_code == 200
    assert "伴奏提取 Admin" in response.text


def test_parent_page_and_health_remain_public(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "secret")

    parent = client.get("/")
    health = client.get("/api/health")

    assert parent.status_code == 200
    assert "伴奏提取" in parent.text
    assert health.status_code == 200
