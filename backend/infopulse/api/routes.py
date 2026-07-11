from __future__ import annotations

import re
import uuid
from dataclasses import asdict
from datetime import date
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..config import load_config
from ..db import get_briefing, get_latest_briefing, sync_categories
from ..orchestrator import generate_async
from .schemas import (
    BriefingResponse,
    CategoryResponse,
    NewsItemResponse,
    RefreshRequest,
    RefreshResponse,
    TaskStatusResponse,
)

router = APIRouter()
_tasks: dict[str, dict[str, Any]] = {}


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories() -> list[CategoryResponse]:
    """获取所有分类及其最新简报摘要。"""
    _, categories = load_config()
    await sync_categories(categories)
    out: list[CategoryResponse] = []
    for cat in categories:
        latest = await get_latest_briefing(cat.id, 1)
        out.append(
            CategoryResponse(
                id=cat.id,
                name=cat.name,
                icon=cat.icon,
                keywords=cat.keywords,
                summary=_summary(latest[0]["content_markdown"]) if latest else "",
            )
        )
    return out


@router.get("/categories/{cat_id}/briefing", response_model=BriefingResponse)
async def get_category_briefing(cat_id: str, date: str | None = None) -> BriefingResponse:
    """获取某分类某日简报（默认最新）。"""
    category = _find_category(cat_id)
    if date:
        row = await get_briefing(cat_id, date)
    else:
        rows = await get_latest_briefing(cat_id, 1)
        row = rows[0] if rows else None
    if row is None:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return _briefing_response(category, row)


@router.post("/categories/{cat_id}/refresh", response_model=RefreshResponse)
async def refresh_category(
    cat_id: str,
    req: RefreshRequest,
    background_tasks: BackgroundTasks,
) -> RefreshResponse:
    """手动触发某分类的简报生成。"""
    _find_category(cat_id)
    try:
        target = date.fromisoformat(req.date) if req.date else None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD") from exc
    task_id = uuid.uuid4().hex
    _tasks[task_id] = {"status": "pending", "error": None}
    background_tasks.add_task(_run_refresh_task, task_id, cat_id, target)
    return RefreshResponse(task_id=task_id, status="pending")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """查询生成任务的运行状态。"""
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        error=task.get("error"),
    )


async def _run_refresh_task(
    task_id: str,
    cat_id: str,
    target: date | None,
) -> None:
    _tasks[task_id] = {"status": "running", "error": None}
    try:
        _, results = await generate_async(target_date=target, category_id=cat_id)
        failed = next((result for result in results if result.status == "failed"), None)
        if failed is not None:
            raise RuntimeError(failed.error or "Briefing generation failed")
        _tasks[task_id] = {"status": "ready", "error": None}
    except Exception as exc:  # noqa: BLE001
        _tasks[task_id] = {"status": "failed", "error": str(exc)}


def _find_category(cat_id: str):
    _, categories = load_config()
    for cat in categories:
        if cat.id == cat_id:
            return cat
    raise HTTPException(status_code=404, detail="Category not found")


def _briefing_response(category, row: dict[str, Any]) -> BriefingResponse:
    sources = [
        NewsItemResponse(
            title=src.get("title", ""),
            media=src.get("media", ""),
            date=src.get("published_at", ""),
            content=src.get("summary", ""),
            url=src.get("url", ""),
        )
        for src in row.get("sources", [])
    ]
    return BriefingResponse(
        report_date=row["report_date"],
        weekday=_weekday(row["report_date"]),
        generated_at=row["generated_at"],
        categories=[
            CategoryResponse(
                **{
                    **asdict(category),
                    "summary": _summary(row.get("content_markdown") or ""),
                }
            )
        ],
        status=row["status"],
        content_markdown=row.get("content_markdown") or "",
        sources=sources,
    )


def _summary(markdown: str) -> str:
    for line in markdown.splitlines():
        text = re.sub(r"^[#=\s·|【】\-\d.]+", "", line).strip()
        if text and not text.startswith("📅"):
            return text[:120]
    return ""


def _weekday(value: str) -> str:
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    try:
        return names[date.fromisoformat(value).weekday()]
    except ValueError:
        return ""
