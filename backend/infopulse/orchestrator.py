from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import clean, deepseek, prompts, rss
from .config import load_config
from .models import Category, CategoryResult, NewsItem
from .settings import settings


def _raw_markdown(cat: Category, items: list[NewsItem], target: date) -> str:
    """不调用大模型时，直接把 RSS 结果排版成 Markdown（省钱/调试用）。"""
    lines = [
        "════════════════════════════════",
        f"📅 {cat.icon} {cat.name} · 每日动态简报（未经AI提炼·RSS原文）",
        f"   报告日期：{target.isoformat()}",
        "════════════════════════════════",
        "",
    ]
    for it in items:
        lines += [
            f"【{it.source}】",
            f"📰 {it.title}",
            f"   来源：{it.source} | 日期：{it.published.isoformat() if it.published else '?'}",
            f"   摘要：{it.summary}",
            f"   链接：{it.url}",
            "",
        ]
    lines.append("════════════════════════════════")
    return "\n".join(lines)


def generate(
    target_date: date | None = None,
    use_llm: bool = True,
    items_override: list[NewsItem] | None = None,
):
    """生成所有分类的简报。

    返回 (target_date, [CategoryResult])。
    items_override 用于测试：直接传入新闻列表，跳过网络抓取。
    """
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()
    if target_date is None:
        target_date = today - timedelta(days=1)

    global_feeds, categories = load_config()

    # 汇总所有唯一 RSS 源（全局 + 各分类专属），每个 URL 只抓一次；
    # 记录 owners：哪些分类“拥有”某个专属源。
    unique_feeds: dict[str, str] = {}   # url -> name
    owners: dict[str, set[str]] = {}    # url -> {category_id}
    for name, url in global_feeds:
        unique_feeds.setdefault(url, name)
    for cat in categories:
        for name, url in cat.feeds:
            unique_feeds.setdefault(url, name)
            owners.setdefault(url, set()).add(cat.id)

    if items_override is not None:
        all_items = items_override
    else:
        all_items = rss.fetch_all([(n, u) for u, n in unique_feeds.items()], tz)

    results: list[CategoryResult] = []
    for cat in categories:
        sel = clean.select_for_category(
            all_items, cat, target_date, settings.max_items_per_category, owners
        )
        result = CategoryResult(category=cat, items=sel)
        if not sel:
            result.status = "empty"
        elif not use_llm:
            result.status = "ready"
            result.markdown = _raw_markdown(cat, sel, target_date)
        else:
            try:
                msgs = prompts.build_messages(cat, sel, target_date, today)
                result.markdown = deepseek.chat(msgs)
                result.status = "ready"
            except Exception as e:  # noqa: BLE001
                result.status = "failed"
                result.error = str(e)
        results.append(result)
    return target_date, results
