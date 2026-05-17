from __future__ import annotations

import secrets
import string
from pathlib import Path

from fastapi import UploadFile

from . import config
from .models import ErrorCode


MAX_UPLOAD_BYTES = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    "mp3": {"audio/mpeg", "audio/mp3", "audio/mpeg3", "audio/x-mpeg-3"},
    "m4a": {"audio/mp4", "audio/x-m4a", "audio/m4a"},
    "wav": {"audio/wav", "audio/x-wav", "audio/wave", "audio/vnd.wav"},
}


def upload_error_code(kind: str) -> ErrorCode:
    if kind == "missing":
        return ErrorCode.UPLOAD_FILE_REQUIRED
    if kind == "empty":
        return ErrorCode.UPLOAD_FILE_EMPTY
    if kind == "type":
        return ErrorCode.UPLOAD_FILE_TYPE_UNSUPPORTED
    return ErrorCode.UPLOAD_FILE_TOO_LARGE


def validate_upload(file: UploadFile | None) -> tuple[str, str]:
    if file is None:
        raise ValueError(upload_error_code("missing").value)
    if not file.filename:
        raise ValueError(upload_error_code("type").value)

    suffix = Path(file.filename).suffix.lower().lstrip(".")
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(upload_error_code("type").value)

    content_type = (file.content_type or "").lower()
    if content_type == "application/octet-stream":
        return suffix, content_type
    if content_type and content_type not in ALLOWED_EXTENSIONS[suffix]:
        raise ValueError(upload_error_code("type").value)
    return suffix, content_type


def random_audio_name(extension: str) -> str:
    alphabet = string.ascii_lowercase + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(12))
    return f"{token}.{extension}"


def save_upload(file: UploadFile, destination: Path) -> int:
    config.ensure_data_dirs()
    total = 0
    chunk_size = 1024 * 1024
    with destination.open("wb") as fh:
        while True:
            chunk = file.file.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                fh.close()
                destination.unlink(missing_ok=True)
                raise ValueError(upload_error_code("large").value)
            fh.write(chunk)
    if total <= 0:
        destination.unlink(missing_ok=True)
        raise ValueError(upload_error_code("empty").value)
    return total
