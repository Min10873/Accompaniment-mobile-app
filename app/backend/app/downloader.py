from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode

import httpx

from . import config
from .models import ErrorCode


def resolve_aweme_url(client: httpx.Client, douyin_url: str) -> str:
    params = urlencode({"url": douyin_url})
    resolve_url = f"{config.SIDECAR_BASE_URL}/api/douyin/web/get_aweme_id?{params}"
    response = client.get(resolve_url)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200 or not data.get("data"):
        raise RuntimeError(ErrorCode.DOWNLOAD_FAILED.value)
    return f"https://www.douyin.com/video/{data['data']}"


def download_video(douyin_url: str, target_path: Path) -> Path:
    config.ensure_data_dirs()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with httpx.Client(timeout=config.DOWNLOAD_TIMEOUT_SECONDS, follow_redirects=True) as client:
            resolved_url = resolve_aweme_url(client, douyin_url)
            params = urlencode(
                {
                    "url": resolved_url,
                    "prefix": "true",
                    "with_watermark": "false",
                }
            )
            download_url = f"{config.SIDECAR_BASE_URL}/api/download?{params}"
            response = client.get(download_url)
            response.raise_for_status()
            reject_sidecar_json_error(response)
            target_path.write_bytes(response.content)
    except (httpx.HTTPError, OSError, ValueError, RuntimeError) as exc:
        raise RuntimeError(ErrorCode.DOWNLOAD_FAILED.value) from exc

    if not target_path.exists() or target_path.stat().st_size <= 0:
        raise RuntimeError(ErrorCode.DOWNLOAD_FAILED.value)
    return target_path


def reject_sidecar_json_error(response: httpx.Response) -> None:
    content_type = response.headers.get("content-type", "")
    content = response.content.lstrip()
    if "application/json" not in content_type and not content.startswith(b"{"):
        return

    data = response.json()
    if data.get("code") != 200:
        raise RuntimeError(ErrorCode.DOWNLOAD_FAILED.value)
