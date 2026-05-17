from pathlib import Path
import secrets
import string

from . import config
from .audio import extract_mp3, pitch_shift_mp3
from .downloader import download_video
from .models import ErrorCode, PitchJobRecord, PitchJobStatus, TaskRecord, TaskStatus
from .task_store import add_pitch_variant, iso_now, load_task, update_pitch_job, update_task


MOCK_MP3_BYTES = (
    b"ID3\x04\x00\x00\x00\x00\x00\x00"
    b"\xff\xfb\x90\x64\x00\x00\x00\x00\x00\x00\x00\x00"
)


def process_task_mock(record: TaskRecord) -> TaskRecord:
    downloading_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(
        update={"downloading_at": downloading_at}
    )
    record = update_task(
        record,
        status=TaskStatus.DOWNLOADING,
        stage_timestamps=timestamps,
    )

    extracting_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(update={"extracting_at": extracting_at})
    record = update_task(
        record,
        status=TaskStatus.EXTRACTING,
        stage_timestamps=timestamps,
    )

    alphabet = string.ascii_lowercase + string.digits
    audio_name = _make_audio_name()
    audio_path = config.AUDIO_DIR / audio_name
    _write_mock_audio(audio_path)

    done_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(update={"done_at": done_at})
    record = update_task(
        record,
        status=TaskStatus.DONE,
        audio_path=str(audio_path.relative_to(config.BASE_DIR)),
        audio_url=f"/files/audio/{audio_name}",
        stage_timestamps=timestamps,
    )
    return _add_original_variant(record)


def _write_mock_audio(path: Path) -> None:
    config.ensure_data_dirs()
    path.write_bytes(MOCK_MP3_BYTES)


def process_task_real(record: TaskRecord) -> TaskRecord:
    video_path = config.VIDEOS_DIR / f"{record.task_id}.mp4"
    audio_name = _make_audio_name()
    audio_path = config.AUDIO_DIR / audio_name

    downloading_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(
        update={"downloading_at": downloading_at}
    )
    record = update_task(
        record,
        status=TaskStatus.DOWNLOADING,
        video_path=str(video_path.relative_to(config.BASE_DIR)),
        stage_timestamps=timestamps,
    )

    try:
        download_video(record.douyin_url, video_path)
    except RuntimeError:
        return _fail_task(record, ErrorCode.DOWNLOAD_FAILED, "download failed")

    extracting_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(update={"extracting_at": extracting_at})
    record = update_task(
        record,
        status=TaskStatus.EXTRACTING,
        audio_path=str(audio_path.relative_to(config.BASE_DIR)),
        audio_url=f"/files/audio/{audio_name}",
        stage_timestamps=timestamps,
    )

    try:
        extract_mp3(video_path, audio_path)
    except RuntimeError:
        return _fail_task(record, ErrorCode.EXTRACT_FAILED, "extract failed")
    finally:
        video_path.unlink(missing_ok=True)

    done_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(update={"done_at": done_at})
    record = update_task(
        record,
        status=TaskStatus.DONE,
        video_path=None,
        stage_timestamps=timestamps,
    )
    return _add_original_variant(record)


def process_pitch_job(task_id: str, pitch_job_id: str) -> TaskRecord | None:
    record = load_task(task_id)
    if record is None:
        return None
    job = record.pitch_jobs.get(pitch_job_id)
    if job is None:
        return record
    if not record.audio_path or not record.audio_url:
        record, _job = _fail_pitch_job(record, job, ErrorCode.SOURCE_AUDIO_MISSING, "source audio missing")
        return record

    source_path = config.BASE_DIR / record.audio_path
    if not source_path.exists() or source_path.stat().st_size <= 0:
        record, _job = _fail_pitch_job(record, job, ErrorCode.SOURCE_AUDIO_MISSING, "source audio missing")
        return record

    record, job = update_pitch_job(
        record,
        job,
        status=PitchJobStatus.PROCESSING,
        started_at=iso_now(),
    )

    audio_name = _make_audio_name()
    audio_path = config.AUDIO_DIR / audio_name
    try:
        if config.MOCK_PROCESSING:
            _write_mock_audio(audio_path)
        else:
            pitch_shift_mp3(source_path, audio_path, job.direction, job.semitones)
    except RuntimeError:
        record, _job = _fail_pitch_job(record, job, ErrorCode.PITCH_FAILED, "pitch failed")
        return record

    relative_path = str(audio_path.relative_to(config.BASE_DIR))
    audio_url = f"/files/audio/{audio_name}"
    record, job = update_pitch_job(
        record,
        job,
        status=PitchJobStatus.DONE,
        done_at=iso_now(),
        audio_path=relative_path,
        audio_url=audio_url,
    )
    return add_pitch_variant(record, job, relative_path, audio_url)


def _fail_task(record: TaskRecord, error_code: ErrorCode, error_detail: str) -> TaskRecord:
    failed_at = iso_now()
    timestamps = record.stage_timestamps.model_copy(update={"failed_at": failed_at})
    return update_task(
        record,
        status=TaskStatus.FAILED,
        error_code=error_code,
        error_detail=error_detail,
        stage_timestamps=timestamps,
    )


def _fail_pitch_job(
    record: TaskRecord,
    job: PitchJobRecord,
    error_code: ErrorCode,
    error_detail: str,
) -> tuple[TaskRecord, PitchJobRecord]:
    return update_pitch_job(
        record,
        job,
        status=PitchJobStatus.FAILED,
        failed_at=iso_now(),
        error_code=error_code,
        error_detail=error_detail,
    )


def _add_original_variant(record: TaskRecord) -> TaskRecord:
    if "original" in record.audio_variants or not record.audio_path or not record.audio_url:
        return record
    from .task_store import ensure_original_variant

    return ensure_original_variant(record)


def _make_audio_name() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12)) + ".mp3"
