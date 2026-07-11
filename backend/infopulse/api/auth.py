"""可选的 Bearer Token 鉴权。

若未配置 API_TOKEN（settings.api_token 为空），则完全放行（MVP 默认）；
配置后，所有依赖 verify_token 的接口需带 `Authorization: Bearer <token>`。
"""
from __future__ import annotations

from fastapi import Header, HTTPException

from ..settings import settings


async def verify_token(authorization: str | None = Header(default=None)) -> None:
    if not settings.api_token:
        return  # 未启用鉴权
    expected = f"Bearer {settings.api_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
