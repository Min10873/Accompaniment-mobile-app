import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR.parent.parent
FRONTEND_DIR = APP_DIR / "frontend"
ADMIN_FRONTEND_DIR = APP_DIR / "admin"
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
AUDIO_DIR = DATA_DIR / "audio"
TASKS_DIR = DATA_DIR / "tasks"

RETENTION_DAYS = 7
SHARE_TEXT_PREVIEW_LIMIT = 80
TASK_ID_LENGTH = 8
APP_VERSION = os.getenv("ACCOMPANIMENT_APP_VERSION", "dev")
MOCK_PROCESSING = os.getenv("ACCOMPANIMENT_MOCK_PROCESSING", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SIDECAR_BASE_URL = os.getenv("ACCOMPANIMENT_SIDECAR_BASE_URL", "http://127.0.0.1:8000")
DOWNLOAD_TIMEOUT_SECONDS = int(os.getenv("ACCOMPANIMENT_DOWNLOAD_TIMEOUT_SECONDS", "180"))
FFMPEG_TIMEOUT_SECONDS = int(os.getenv("ACCOMPANIMENT_FFMPEG_TIMEOUT_SECONDS", "180"))
ADMIN_USERNAME = os.getenv("ACCOMPANIMENT_ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ACCOMPANIMENT_ADMIN_PASSWORD", "")


def ensure_data_dirs() -> None:
    for path in (VIDEOS_DIR, AUDIO_DIR, TASKS_DIR):
        path.mkdir(parents=True, exist_ok=True)
