import pytest

from app.link_parser import extract_douyin_url


def test_extract_douyin_url_from_share_text():
    text = "复制打开抖音 https://v.douyin.com/VUkeE3kU-o8/ PkP:/"
    assert extract_douyin_url(text) == "https://v.douyin.com/VUkeE3kU-o8/"


def test_extract_first_douyin_url():
    text = "先看 https://v.douyin.com/abc123/ 再看 https://v.douyin.com/xyz789/"
    assert extract_douyin_url(text) == "https://v.douyin.com/abc123/"


def test_extract_douyin_url_raises_when_missing():
    with pytest.raises(ValueError, match="没有找到抖音链接"):
        extract_douyin_url("这里没有链接")
