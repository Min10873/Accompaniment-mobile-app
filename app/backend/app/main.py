import base64
import secrets

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .admin import admin_status, admin_tasks
from . import config
from .link_parser import extract_douyin_url
from .models import ErrorCode, PitchCreateRequest, PitchJobStatus, PitchResponse, TaskCreateRequest, TaskResponse, TaskStatus
from .task_store import create_task as create_task_record
from .task_store import (
    cached_variant,
    create_pitch_job,
    ensure_original_variant,
    expire_if_needed,
    has_active_task,
    load_task,
    variant_key,
)
from .worker import process_pitch_job, process_task_mock, process_task_real


app = FastAPI(title="Accompaniment App")
config.ensure_data_dirs()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files/audio", StaticFiles(directory=config.AUDIO_DIR), name="audio")


def is_admin_path(path: str) -> bool:
    return path == "/admin" or path.startswith("/admin/") or path.startswith("/api/admin/")


def admin_auth_challenge(status_code: int) -> Response:
    return Response(
        status_code=status_code,
        headers={"WWW-Authenticate": 'Basic realm="Accompaniment Admin"'},
    )


def has_valid_admin_auth(authorization: str | None) -> bool:
    if not config.ADMIN_USERNAME or not config.ADMIN_PASSWORD:
        return False
    if not authorization or not authorization.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(authorization.removeprefix("Basic "), validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return False
    username, separator, password = decoded.partition(":")
    if not separator:
        return False
    return secrets.compare_digest(username, config.ADMIN_USERNAME) and secrets.compare_digest(
        password,
        config.ADMIN_PASSWORD,
    )


@app.middleware("http")
async def protect_admin(request: Request, call_next):
    if not is_admin_path(request.url.path):
        return await call_next(request)
    if not config.ADMIN_USERNAME or not config.ADMIN_PASSWORD:
        return admin_auth_challenge(503)
    if not has_valid_admin_auth(request.headers.get("authorization")):
        return admin_auth_challenge(401)
    return await call_next(request)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": config.APP_VERSION,
        "processing_mode": "mock" if config.MOCK_PROCESSING else "real",
    }


@app.get("/api/admin/status")
def get_admin_status() -> dict:
    return admin_status()


@app.get("/api/admin/tasks")
def get_admin_tasks() -> dict:
    return admin_tasks()


@app.post("/api/tasks")
def create_task(payload: TaskCreateRequest, background_tasks: BackgroundTasks) -> JSONResponse:
    try:
        douyin_url = extract_douyin_url(payload.share_text)
    except ValueError:
        return api_response(
            422,
            TaskResponse(
                task_id=None,
                status=None,
                error_code=ErrorCode.NO_DOUYIN_URL,
                message="没有找到抖音链接，请重新复制分享文本",
            ),
        )

    if has_active_task():
        return api_response(
            503,
            TaskResponse(
                task_id=None,
                status=None,
                error_code=ErrorCode.SERVER_BUSY,
                message="现在处理的人有点多，请稍后再试",
            ),
        )

    record = create_task_record(payload.share_text, douyin_url)
    background_tasks.add_task(process_task, record.task_id)

    return api_response(
        201,
        TaskResponse(
            task_id=record.task_id,
            status=TaskStatus.QUEUED,
            message="已开始处理",
        ),
    )


@app.post("/api/tasks/{task_id}/pitch")
def create_pitch(task_id: str, payload: PitchCreateRequest, background_tasks: BackgroundTasks) -> JSONResponse:
    record = load_task(task_id)
    if record is None:
        return pitch_api_response(
            404,
            PitchResponse(
                task_id=task_id,
                status=None,
                error_code=ErrorCode.TASK_NOT_FOUND,
                message="没有找到这次任务，请重新提交",
            ),
        )

    record = expire_if_needed(record)
    if record.status == TaskStatus.EXPIRED:
        return pitch_api_response(
            409,
            PitchResponse(
                task_id=task_id,
                status=TaskStatus.EXPIRED,
                error_code=ErrorCode.TASK_EXPIRED,
                message="这个链接已经过期，请重新提取一次",
            ),
        )
    if record.status != TaskStatus.DONE:
        return pitch_api_response(
            409,
            PitchResponse(
                task_id=task_id,
                status=record.status,
                error_code=ErrorCode.SOURCE_NOT_READY,
                message="原调音频还没有准备好",
            ),
        )
    if not record.audio_path or not record.audio_url:
        return pitch_api_response(
            409,
            PitchResponse(
                task_id=task_id,
                status=record.status,
                error_code=ErrorCode.SOURCE_AUDIO_MISSING,
                message="没有找到原调音频，请重新提取一次",
            ),
        )

    record = ensure_original_variant(record)
    key = variant_key(payload.direction.value, payload.semitones)
    variant = cached_variant(record, key)
    if variant is not None:
        return pitch_api_response(
            200,
            PitchResponse(
                task_id=task_id,
                pitch_job_id=None,
                status=PitchJobStatus.DONE,
                variant_key=key,
                audio_url=variant.audio_url,
                cached=True,
                message="这个变调版本已经生成过，可以直接播放",
            ),
        )

    if has_active_task():
        return pitch_api_response(
            503,
            PitchResponse(
                task_id=task_id,
                status=None,
                variant_key=key,
                error_code=ErrorCode.SERVER_BUSY,
                message="现在处理的人有点多，请稍后再试",
            ),
        )

    record, job = create_pitch_job(record, payload)
    background_tasks.add_task(process_pitch_job, record.task_id, job.pitch_job_id)
    direction_label = "升调" if payload.direction.value == "up" else "降调"
    return pitch_api_response(
        202,
        PitchResponse(
            task_id=task_id,
            pitch_job_id=job.pitch_job_id,
            status=PitchJobStatus.QUEUED,
            variant_key=job.variant_key,
            message=f"正在生成{direction_label} {payload.semitones} 个半音版本",
        ),
    )


@app.get("/api/tasks/{task_id}/pitch/{pitch_job_id}")
def get_pitch(task_id: str, pitch_job_id: str) -> JSONResponse:
    record = load_task(task_id)
    if record is None:
        return pitch_api_response(
            404,
            PitchResponse(
                task_id=task_id,
                pitch_job_id=pitch_job_id,
                status=None,
                error_code=ErrorCode.TASK_NOT_FOUND,
                message="没有找到这次任务，请重新提交",
            ),
        )
    job = record.pitch_jobs.get(pitch_job_id)
    if job is None:
        return pitch_api_response(
            404,
            PitchResponse(
                task_id=task_id,
                pitch_job_id=pitch_job_id,
                status=None,
                error_code=ErrorCode.PITCH_JOB_NOT_FOUND,
                message="没有找到这次变调任务",
            ),
        )

    if job.status == PitchJobStatus.DONE:
        message = "变调好了，可以播放"
    elif job.status == PitchJobStatus.FAILED:
        message = "这次变调没有成功，原调还可以继续播放"
    else:
        message = "正在生成变调版本"
    return pitch_api_response(
        200,
        PitchResponse(
            task_id=task_id,
            pitch_job_id=job.pitch_job_id,
            status=job.status,
            variant_key=job.variant_key,
            audio_url=job.audio_url,
            error_code=job.error_code,
            message=message,
        ),
    )


def process_task(task_id: str) -> None:
    record = load_task(task_id)
    if record is None:
        return
    if config.MOCK_PROCESSING:
        process_task_mock(record)
    else:
        process_task_real(record)


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str) -> JSONResponse:
    record = load_task(task_id)
    if record is None:
        return api_response(
            404,
            TaskResponse(
                task_id=task_id,
                status=None,
                error_code=ErrorCode.TASK_NOT_FOUND,
                message="没有找到这次任务，请重新提交",
            ),
        )

    record = expire_if_needed(record)
    return api_response(200, response_for_record(record))


def response_for_record(record) -> TaskResponse:
    if record.status == TaskStatus.DONE:
        record = ensure_original_variant(record)
        return TaskResponse(
            task_id=record.task_id,
            status=record.status,
            audio_url=record.audio_url,
            audio_variants=record.audio_variants,
            message="处理好了，点击下面链接播放",
        )
    if record.status == TaskStatus.EXPIRED:
        return TaskResponse(
            task_id=record.task_id,
            status=record.status,
            error_code=ErrorCode.TASK_EXPIRED,
            message="这个链接已经过期，请重新提取一次",
        )
    if record.status == TaskStatus.FAILED:
        return TaskResponse(
            task_id=record.task_id,
            status=record.status,
            error_code=record.error_code or ErrorCode.INTERNAL_ERROR,
            message="这次没有处理成功，请换一个视频试试",
        )
    return TaskResponse(
        task_id=record.task_id,
        status=record.status,
        message="正在处理，请稍等",
    )


def api_response(status_code: int, body: TaskResponse) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
    )


def pitch_api_response(status_code: int, body: PitchResponse) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
    )


if config.ADMIN_FRONTEND_DIR.exists():
    app.mount("/admin", StaticFiles(directory=config.ADMIN_FRONTEND_DIR, html=True), name="admin")

if config.FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")
