from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta

from . import clean, deepseek, prompts, rss
from .config import load_config
from .db import save_briefing, sync_categories
from .models import Category, CategoryResult, NewsItem
from .search import BochaProvider, RssProvider, merge_results
from .settings import settings
from .tz import get_tz


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
    tz = get_tz(settings.timezone)
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


async def generate_async(
    target_date: date | None = None,
    use_llm: bool = True,
    use_search: bool = True,
    category_id: str | None = None,
) -> tuple[date, list[CategoryResult]]:
    """生成简报并写入 SQLite，供 API/后台任务调用。

    保留同步 generate() 给命令行使用；这里把阻塞网络和 LLM 调用放到线程中，
    避免卡住 FastAPI 事件循环。
    """
    tz = get_tz(settings.timezone)
    today = datetime.now(tz).date()
    if target_date is None:
        target_date = today - timedelta(days=1)

    global_feeds, categories = load_config()
    if category_id:
        categories = [cat for cat in categories if cat.id == category_id]
    await sync_categories(categories)

    unique_feeds, owners = _collect_feeds(global_feeds, categories)
    all_items: list[NewsItem] = []
    if use_search:
        all_items = await _search_items(unique_feeds, categories, target_date)
    else:
        all_items = await asyncio.to_thread(
            rss.fetch_all,
            [(name, url) for url, name in unique_feeds.items()],
            tz,
        )

    generated_at = datetime.now(tz).isoformat(timespec="seconds")
    results: list[CategoryResult] = []
    for cat in categories:
        selected = clean.select_for_category(
            all_items,
            cat,
            target_date,
            settings.max_items_per_category,
            owners,
        )
        result = await _build_result(cat, selected, target_date, today, use_llm)
        await save_briefing(result, target_date.isoformat(), generated_at, settings.deepseek_model)
        results.append(result)
    return target_date, results


def _collect_feeds(
    global_feeds: list[tuple[str, str]],
    categories: list[Category],
) -> tuple[dict[str, str], dict[str, set[str]]]:
    unique_feeds: dict[str, str] = {}
    owners: dict[str, set[str]] = {}
    for name, url in global_feeds:
        unique_feeds.setdefault(url, name)
    for cat in categories:
        for name, url in cat.feeds:
            unique_feeds.setdefault(url, name)
            owners.setdefault(url, set()).add(cat.id)
    return unique_feeds, owners


async def _search_items(
    unique_feeds: dict[str, str],
    categories: list[Category],
    target_date: date,
) -> list[NewsItem]:
    providers = []
    if settings.bocha_api_key:
        providers.append(BochaProvider(settings.bocha_api_key, settings.bocha_base_url))
    rss_provider = RssProvider([(name, url) for url, name in unique_feeds.items()])

    queries = [_category_query(cat) for cat in categories]
    search_tasks = [
        merge_results(
            providers,
            query,
            target_date,
            settings.max_items_per_category,
        )
        for query in queries
        if query and providers
    ]
    search_tasks.append(rss_provider.search("*", target_date, settings.max_items_per_category * 4))
    batches = await asyncio.gather(*search_tasks)
    merged = [item for batch in batches for item in batch]
    return clean.dedupe(merged)


def _category_query(cat: Category) -> str:
    if not cat.keywords:
        return cat.name
    return " ".join(cat.keywords[:8])


async def _build_result(
    cat: Category,
    selected: list[NewsItem],
    target_date: date,
    today: date,
    use_llm: bool,
) -> CategoryResult:
    result = CategoryResult(category=cat, items=selected)
    if not selected:
        result.status = "empty"
    elif not use_llm:
        result.status = "ready"
        result.markdown = _raw_markdown(cat, selected, target_date)
    else:
        try:
            msgs = prompts.build_messages(cat, selected, target_date, today)
            result.markdown = await asyncio.to_thread(deepseek.chat, msgs)
            result.status = "ready"
        except Exception as e:  # noqa: BLE001
            result.status = "failed"
            result.error = str(e)
    return result
