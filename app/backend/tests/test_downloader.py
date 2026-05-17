from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app import config
from app.downloader import download_video
from app.models import ErrorCode


ORIGINAL_HTTPX_CLIENT = httpx.Client


def mock_client_factory(transport):
    def create_client(**kwargs):
        return ORIGINAL_HTTPX_CLIENT(transport=transport, **kwargs)

    return create_client


def test_download_video_resolves_short_link_before_download(monkeypatch, tmp_path):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path == "/api/douyin/web/get_aweme_id":
            return httpx.Response(200, json={"code": 200, "data": "7635292206111218138"})
        if request.url.path == "/api/download":
            params = parse_qs(urlparse(str(request.url)).query)
            assert params["url"] == ["https://www.douyin.com/video/7635292206111218138"]
            return httpx.Response(200, headers={"content-type": "video/mp4"}, content=b"mp4-bytes")
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(httpx, "Client", mock_client_factory(transport))

    target_path = tmp_path / "video.mp4"
    result = download_video("https://v.douyin.com/bMs3D8QlEQY/", target_path)

    assert result == target_path
    assert target_path.read_bytes() == b"mp4-bytes"
    assert requests[0].startswith(f"{config.SIDECAR_BASE_URL}/api/douyin/web/get_aweme_id")
    assert requests[1].startswith(f"{config.SIDECAR_BASE_URL}/api/download")


def test_download_video_rejects_sidecar_json_error(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/douyin/web/get_aweme_id":
            return httpx.Response(200, json={"code": 200, "data": "7635292206111218138"})
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"code": 400, "message": "", "router": "/api/download"},
        )

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(httpx, "Client", mock_client_factory(transport))

    with pytest.raises(RuntimeError, match=ErrorCode.DOWNLOAD_FAILED.value):
        download_video("https://v.douyin.com/bMs3D8QlEQY/", tmp_path / "video.mp4")

    assert not (tmp_path / "video.mp4").exists()


def test_download_video_rejects_aweme_resolution_error(monkeypatch, tmp_path):
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"code": 400, "data": None})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(httpx, "Client", mock_client_factory(transport))

    with pytest.raises(RuntimeError, match=ErrorCode.DOWNLOAD_FAILED.value):
        download_video("https://v.douyin.com/bMs3D8QlEQY/", tmp_path / "video.mp4")
