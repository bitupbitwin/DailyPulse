from __future__ import annotations

import asyncio
import json
import re
import urllib.error
import urllib.request
from datetime import date, datetime
from typing import Any, Protocol

from . import clean, rss
from .models import NewsItem
from .settings import settings
from .tz import get_tz


class SearchProvider(Protocol):
    """统一搜索接口：所有搜索源的抽象。"""

    async def search(
        self,
        query: str,
        target_date: date,
        max_results: int,
    ) -> list[NewsItem]: ...


class BochaProvider:
    """博查 AI 搜索（主搜索源），国内直连。"""

    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    async def search(
        self,
        query: str,
        target_date: date,
        max_results: int = 10,
    ) -> list[NewsItem]:
        return await asyncio.to_thread(
            self._search_sync,
            query,
            target_date,
            max_results,
        )

    def _search_sync(
        self,
        query: str,
        target_date: date,
        max_results: int,
    ) -> list[NewsItem]:
        # 检索时间窗默认对齐目标日期（T-1 当天）；博查支持传具体日期。
        # 若某些账号/版本对日期格式要求不同，可用环境变量 BOCHA_FRESHNESS 覆盖
        # （如 "oneDay" / "oneWeek"）。无论窗口多大，下面 _bocha_to_news 都会按
        # 目标日期做代码层硬过滤，保证只保留当天新闻。
        freshness = settings.bocha_freshness or target_date.isoformat()
        payload = {
            "query": query,
            "freshness": freshness,
            "count": max_results,
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{self._base_url}/web-search",
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "User-Agent": "InfoPulse/0.2",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=settings.http_timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Bocha search failed: HTTP {exc.code} {detail[:200]}") from exc

        return [
            item
            for item in (_bocha_to_news(raw, target_date) for raw in _extract_web_items(data))
            if item is not None
        ][:max_results]


class RssProvider:
    """RSS 搜索（辅搜索源），将已有 rss.py 逻辑包装为 SearchProvider。"""

    def __init__(self, feeds: list[tuple[str, str]]) -> None:
        self._feeds = feeds

    async def search(
        self,
        query: str,
        target_date: date,
        max_results: int = 25,
    ) -> list[NewsItem]:
        tz = get_tz(settings.timezone)
        items = await asyncio.to_thread(rss.fetch_all, self._feeds, tz)
        if query == "*":
            return clean.dedupe(clean.filter_by_date(items, target_date))[:max_results]
        query_terms = [term for term in re.split(r"\s+", query.lower()) if term]
        filtered = [
            item
            for item in clean.filter_by_date(items, target_date)
            if not query_terms
            or any(term in f"{item.title} {item.summary}".lower() for term in query_terms)
        ]
        return clean.dedupe(filtered)[:max_results]


async def merge_results(
    providers: list[SearchProvider],
    query: str,
    target_date: date,
    max_results: int,
) -> list[NewsItem]:
    """并发调用多个 Provider，合并结果并去重。"""
    tasks = [p.search(query, target_date, max_results) for p in providers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    merged: list[NewsItem] = []
    for result in results:
        if isinstance(result, list):
            merged.extend(result)
        elif isinstance(result, Exception):
            print(f"[warn] Provider failed: {result}")
    return clean.dedupe(merged)[:max_results]


def _extract_web_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: Any = data
    for key in ("data", "webPages"):
        if isinstance(candidates, dict) and key in candidates:
            candidates = candidates[key]
    if isinstance(candidates, dict):
        for key in ("value", "results", "items"):
            if isinstance(candidates.get(key), list):
                return candidates[key]
    if isinstance(data.get("results"), list):
        return data["results"]
    if isinstance(data.get("items"), list):
        return data["items"]
    return []


def _bocha_to_news(raw: dict[str, Any], target_date: date) -> NewsItem | None:
    title = str(raw.get("title") or raw.get("name") or "").strip()
    url = str(raw.get("url") or raw.get("link") or "").strip()
    if not title or not url:
        return None

    published = _parse_bocha_date(
        str(
            raw.get("date")
            or raw.get("dateLastCrawled")
            or raw.get("published_at")
            or raw.get("publishedAt")
            or raw.get("datePublished")
            or ""
        )
    )
    # 日期硬过滤（对应开发说明书 §8.1）：解析不到日期、或日期≠目标日期的条目一律丢弃，
    # 绝不把无日期结果当作目标日期收录（此前的 bug）。
    if published is None or published != target_date:
        return None

    summary = str(raw.get("summary") or raw.get("snippet") or raw.get("description") or "")
    source = str(raw.get("siteName") or raw.get("source") or raw.get("provider") or "Bocha").strip()
    return NewsItem(
        title=title,
        url=url,
        source=source or "Bocha",
        published=published,
        summary=summary.strip()[:400],
        feed_url="bocha://web-search",
    )


def _parse_bocha_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.date()
    except ValueError:
        pass
    match = re.search(r"\d{4}-\d{1,2}-\d{1,2}", value)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(0))
    except ValueError:
        return None
