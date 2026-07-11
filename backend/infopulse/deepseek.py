from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from .settings import settings


class DeepSeekError(Exception):
    pass


def _call_once(base_url: str, api_key: str, model: str, messages: list[dict],
               temperature: float, timeout: int) -> str:
    """向一个 OpenAI 兼容端点发一次请求，返回文本内容。"""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        raise DeepSeekError(f"LLM API 返回 {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise DeepSeekError(f"网络错误（无法连接 LLM 网关）: {e}") from e

    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise DeepSeekError(f"LLM 响应格式异常: {json.dumps(body)[:300]}") from e


def chat(messages: list[dict], model: str | None = None, temperature: float = 0.3,
         timeout: int = 120, retries: int = 2) -> str:
    """调用 DeepSeek（OpenAI 兼容 /chat/completions），返回文本内容。仅用标准库。

    健壮性（对应开发说明书 §4.3）：
    - 主端点失败自动重试 retries 次（指数退避）；
    - 全部失败后，若配置了 FALLBACK_* 备用网关（如硅基流动），降级到备用网关再试。
    """
    if not settings.deepseek_api_key:
        raise DeepSeekError("缺少 DEEPSEEK_API_KEY，请在 backend/.env 中配置")

    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return _call_once(
                settings.deepseek_base_url,
                settings.deepseek_api_key,
                model or settings.deepseek_model,
                messages, temperature, timeout,
            )
        except DeepSeekError as e:
            last_err = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))  # 1.5s, 3s 退避

    # 主端点彻底失败 → 尝试备用网关
    if settings.fallback_base_url and settings.fallback_api_key:
        try:
            return _call_once(
                settings.fallback_base_url,
                settings.fallback_api_key,
                settings.fallback_model or model or settings.deepseek_model,
                messages, temperature, timeout,
            )
        except DeepSeekError as e:
            raise DeepSeekError(f"主/备用 LLM 均失败；备用错误：{e}；主错误：{last_err}") from e

    raise DeepSeekError(str(last_err))
