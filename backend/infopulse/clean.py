from __future__ import annotations

from datetime import date

from .models import Category, NewsItem


def filter_by_date(items: list[NewsItem], target: date) -> list[NewsItem]:
    """日期硬过滤：只保留发布日期 == 目标日期的新闻（缺日期的已是 None，自动排除）。"""
    return [it for it in items if it.published == target]


def dedupe(items: list[NewsItem]) -> list[NewsItem]:
    seen: set[str] = set()
    out: list[NewsItem] = []
    for it in items:
        key = (it.url or it.title).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def match_category(items: list[NewsItem], cat: Category) -> list[NewsItem]:
    """按关键词命中标题/摘要，归入该分类。"""
    kws = [k.lower() for k in cat.keywords if k]
    res = []
    for it in items:
        hay = f"{it.title} {it.summary}".lower()
        if any(k in hay for k in kws):
            res.append(it)
    return res


def select_for_category(
    all_items: list[NewsItem], cat: Category, target: date, limit: int
) -> list[NewsItem]:
    """组合：日期过滤 → 关键词归类 → 去重 → 截断 Top N。"""
    items = filter_by_date(all_items, target)
    items = match_category(items, cat)
    items = dedupe(items)
    return items[:limit]
