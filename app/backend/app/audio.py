from __future__ import annotations

import subprocess
from pathlib import Path
import tempfile

from . import config
from .models import ErrorCode, PitchDirection


METADATA_COMMENT = "from LFAPP"


def extract_mp3(video_path: Path, target_path: Path, title: str | None = None) -> Path:
    config.ensure_data_dirs()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-q:a",
        "4",
        "-metadata",
        f"comment={METADATA_COMMENT}",
        "-metadata",
        f"title={title or '抖音伴奏'}",
        str(target_path),
    ]
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=config.FFMPEG_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(ErrorCode.EXTRACT_FAILED.value) from exc

    if not target_path.exists() or target_path.stat().st_size <= 0:
        raise RuntimeError(ErrorCode.EXTRACT_FAILED.value)
    return target_path


def pitch_shift_mp3(
    source_path: Path,
    target_path: Path,
    direction: PitchDirection,
    semitones: int,
    title: str | None = None,
) -> Path:
    config.ensure_data_dirs()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    signed_semitones = semitones if direction == PitchDirection.UP else -semitones
    pitch_ratio = 2 ** (signed_semitones / 12)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-af",
        f"rubberband=pitch={pitch_ratio:.8f}",
        "-acodec",
        "libmp3lame",
        "-q:a",
        "4",
        "-metadata",
        f"comment={METADATA_COMMENT}",
        "-metadata",
        f"title={title or '伴奏'}",
        str(target_path),
    ]
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=config.FFMPEG_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(ErrorCode.PITCH_FAILED.value) from exc

    if not target_path.exists() or target_path.stat().st_size <= 0:
        raise RuntimeError(ErrorCode.PITCH_FAILED.value)
    return target_path


def add_audio_metadata(path: Path, title: str | None = None) -> bool:
    if not path.exists() or path.stat().st_size <= 0:
        return False

    with tempfile.NamedTemporaryFile(
        suffix=path.suffix,
        prefix=f"{path.stem}-meta-",
        dir=path.parent,
        delete=False,
    ) as tmp:
        tmp_path = Path(tmp.name)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(path),
        "-map",
        "0",
        "-c",
        "copy",
        "-metadata",
        f"comment={METADATA_COMMENT}",
        "-metadata",
        f"title={title or '上传的音频'}",
        str(tmp_path),
    ]
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=config.FFMPEG_TIMEOUT_SECONDS,
        )
        if tmp_path.exists() and tmp_path.stat().st_size > 0:
            tmp_path.replace(path)
            return True
    except (OSError, subprocess.SubprocessError):
        pass
    tmp_path.unlink(missing_ok=True)
    return False
