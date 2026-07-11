from __future__ import annotations

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: str
    keywords: list[str]
    summary: str = ""


class NewsItemResponse(BaseModel):
    tag: str = ""
    title: str
    media: str
    date: str
    content: str
    extra: str = ""
    url: str = ""


class BriefingResponse(BaseModel):
    report_date: str
    weekday: str
    generated_at: str
    categories: list[CategoryResponse]
    status: str
    content_markdown: str = ""
    sources: list[NewsItemResponse] = []


class RefreshRequest(BaseModel):
    date: str | None = None


class RefreshResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    error: str | None = None


class SourceItem(BaseModel):
    title: str
    media: str
    url: str
    published_at: str


class AskRequest(BaseModel):
    question: str
    date: str | None = None  # 针对某日简报追问；默认最新


class AskResponse(BaseModel):
    answer: str
    model: str = ""
