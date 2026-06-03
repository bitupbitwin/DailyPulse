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
    all_items: list[NewsItem],
    cat: Category,
    target: date,
    limit: int,
    owners: dict[str, set[str]] | None = None,
) -> list[NewsItem]:
    """组合：日期过滤 →（专属源归属 或 关键词命中）→ 去重 → 截断 Top N。

    owners: feed_url -> {拥有该源的分类 id}。来自分类专属源的新闻直接归入该分类
    （无需关键词命中）；其余新闻仍按关键词路由。owners 为 None 时退化为纯关键词模式。
    """
    owners = owners or {}
    kws = [k.lower() for k in cat.keywords if k]

    selected: list[NewsItem] = []
    for it in filter_by_date(all_items, target):
        owned = cat.id in owners.get(it.feed_url, set())
        if owned or _keyword_hit(it, kws):
            selected.append(it)
    return dedupe(selected)[:limit]


def _keyword_hit(item: NewsItem, lowered_keywords: list[str]) -> bool:
    if not lowered_keywords:
        return False
    hay = f"{item.title} {item.summary}".lower()
    return any(k in hay for k in lowered_keywords)
