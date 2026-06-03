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

    feeds, categories = load_config()
    all_items = items_override if items_override is not None else rss.fetch_all(feeds, tz)

    results: list[CategoryResult] = []
    for cat in categories:
        sel = clean.select_for_category(all_items, cat, target_date, settings.max_items_per_category)
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
