from __future__ import annotations

import json
import urllib.error
import urllib.request

from .settings import settings


class DeepSeekError(Exception):
    pass


def chat(messages: list[dict], model: str | None = None, temperature: float = 0.3,
         timeout: int = 120) -> str:
    """调用 DeepSeek（OpenAI 兼容 /chat/completions），返回文本内容。仅用标准库。"""
    if not settings.deepseek_api_key:
        raise DeepSeekError("缺少 DEEPSEEK_API_KEY，请在 backend/.env 中配置")

    url = settings.deepseek_base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model or settings.deepseek_model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        raise DeepSeekError(f"DeepSeek API 返回 {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise DeepSeekError(f"网络错误（无法连接 DeepSeek）: {e}") from e

    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise DeepSeekError(f"DeepSeek 响应格式异常: {json.dumps(body)[:300]}") from e
