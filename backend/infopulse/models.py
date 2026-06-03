from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class NewsItem:
    """一条新闻（来自 RSS）。"""
    title: str
    url: str
    source: str            # 来源媒体
    published: date | None  # 解析后的发布日期；解析不到则为 None（会被丢弃）
    summary: str           # 摘要（已去 HTML）
    feed_url: str = ""     # 该条来自哪个 RSS 源（用于分类专属源归属）


@dataclass
class Category:
    """一个分类的配置。"""
    id: str
    name: str
    icon: str
    keywords: list[str]
    output_format: str | None = None  # 可在 yaml 里覆盖输出格式；为空则用 prompts.py 默认
    feeds: list[tuple[str, str]] = field(default_factory=list)  # 该分类专属 RSS 源 (name, url)


@dataclass
class CategoryResult:
    """一个分类的生成结果。"""
    category: Category
    items: list[NewsItem] = field(default_factory=list)
    markdown: str = ""
    status: str = "pending"        # ready | empty | failed
    error: str | None = None
