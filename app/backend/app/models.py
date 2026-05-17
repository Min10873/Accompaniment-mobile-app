from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    EXTRACTING = "extracting"
    DONE = "done"
    FAILED = "failed"
    EXPIRED = "expired"


class PitchDirection(StrEnum):
    UP = "up"
    DOWN = "down"


class PitchJobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ErrorCode(StrEnum):
    NO_DOUYIN_URL = "NO_DOUYIN_URL"
    SERVER_BUSY = "SERVER_BUSY"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_EXPIRED = "TASK_EXPIRED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    EXTRACT_FAILED = "EXTRACT_FAILED"
    PROCESS_TIMEOUT = "PROCESS_TIMEOUT"
    INVALID_PITCH_REQUEST = "INVALID_PITCH_REQUEST"
    SOURCE_NOT_READY = "SOURCE_NOT_READY"
    SOURCE_AUDIO_MISSING = "SOURCE_AUDIO_MISSING"
    PITCH_JOB_NOT_FOUND = "PITCH_JOB_NOT_FOUND"
    PITCH_FAILED = "PITCH_FAILED"
    PITCH_TIMEOUT = "PITCH_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class TaskCreateRequest(BaseModel):
    share_text: str = Field(default="")


class TaskResponse(BaseModel):
    task_id: str | None
    status: TaskStatus | None
    audio_url: str | None = None
    audio_variants: dict[str, "AudioVariant"] | None = None
    error_code: ErrorCode | None = None
    message: str


class PitchCreateRequest(BaseModel):
    direction: PitchDirection
    semitones: int = Field(ge=1, le=11)


class PitchResponse(BaseModel):
    task_id: str | None
    pitch_job_id: str | None = None
    status: PitchJobStatus | TaskStatus | None
    variant_key: str | None = None
    audio_url: str | None = None
    cached: bool = False
    error_code: ErrorCode | None = None
    message: str


class StageTimestamps(BaseModel):
    queued_at: str
    downloading_at: str | None = None
    extracting_at: str | None = None
    done_at: str | None = None
    failed_at: str | None = None


class AudioVariant(BaseModel):
    kind: str
    audio_path: str
    audio_url: str
    created_at: str
    direction: PitchDirection | None = None
    semitones: int | None = None
    source: str | None = None
    label: str


class PitchJobRecord(BaseModel):
    pitch_job_id: str
    status: PitchJobStatus
    variant_key: str
    direction: PitchDirection
    semitones: int
    created_at: str
    updated_at: str
    started_at: str | None = None
    done_at: str | None = None
    failed_at: str | None = None
    audio_path: str | None = None
    audio_url: str | None = None
    error_code: ErrorCode | None = None
    error_detail: str | None = None


class TaskRecord(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: str
    updated_at: str
    expires_at: str
    share_text_preview: str
    douyin_url: str
    video_path: str | None = None
    audio_path: str | None = None
    audio_url: str | None = None
    audio_variants: dict[str, AudioVariant] = Field(default_factory=dict)
    pitch_jobs: dict[str, PitchJobRecord] = Field(default_factory=dict)
    error_code: ErrorCode | None = None
    error_detail: str | None = None
    stage_timestamps: StageTimestamps

    def is_expired_at(self, now: datetime) -> bool:
        if self.status == TaskStatus.EXPIRED:
            return True
        expires = datetime.fromisoformat(self.expires_at)
        return self.status == TaskStatus.DONE and now >= expires
