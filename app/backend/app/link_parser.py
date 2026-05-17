import re


DOUYIN_URL_RE = re.compile(r"https?://v\.douyin\.com/[A-Za-z0-9_-]+/?")
NO_DOUYIN_URL_MESSAGE = "没有找到抖音链接，请重新复制分享文本"


def extract_douyin_url(text: str) -> str:
    match = DOUYIN_URL_RE.search(text or "")
    if not match:
        raise ValueError(NO_DOUYIN_URL_MESSAGE)
    return match.group(0)
