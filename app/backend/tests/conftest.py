import sys
import shutil
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import config


@pytest.fixture(autouse=True)
def clean_data_dirs():
    for path in (config.VIDEOS_DIR, config.AUDIO_DIR, config.TASKS_DIR):
        shutil.rmtree(path, ignore_errors=True)
    config.ensure_data_dirs()
    yield
    for path in (config.VIDEOS_DIR, config.AUDIO_DIR, config.TASKS_DIR):
        shutil.rmtree(path, ignore_errors=True)
    config.ensure_data_dirs()
