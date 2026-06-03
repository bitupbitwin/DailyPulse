from __future__ import annotations

import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from .models import NewsItem
from .settings import settings

UA = "Mozilla/5.0 (InfoPulse RSS Reader)"
ATOM = "{http://www.w3.org/2005/Atom}"
_UTC = ZoneInfo("UTC")


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=settings.http_timeout) as resp:
        return resp.read()


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s[:400]


def _parse_date(s: str, tz: ZoneInfo) -> date | None:
    """解析 RSS 的 RFC822 或 Atom 的 ISO8601 时间，转成目标时区下的日期。"""
    s = (s or "").strip()
    if not s:
        return None
    dt: datetime | None = None
    try:
        dt = parsedate_to_datetime(s)  # RFC822, e.g. "Mon, 02 Jun 2026 10:00:00 +0800"
    except (TypeError, ValueError, IndexError):
        dt = None
    if dt is None:
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))  # ISO8601
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_UTC)
    return dt.astimezone(tz).date()


def parse_feed(content: bytes, source_default: str, tz: ZoneInfo) -> list[NewsItem]:
    """解析 RSS 或 Atom 内容为 NewsItem 列表（标准库实现）。"""
    items: list[NewsItem] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return items

    channel = root.find("channel")
    if channel is not None:  # RSS 2.0
        src = _text(channel.find("title")) or source_default
        for it in channel.findall("item"):
            items.append(
                NewsItem(
                    title=_text(it.find("title")),
                    url=_text(it.find("link")),
                    source=src,
                    published=_parse_date(_text(it.find("pubDate")), tz),
                    summary=_strip_html(_text(it.find("description"))),
                )
            )
    else:  # Atom
        src = _text(root.find(ATOM + "title")) or source_default
        for e in root.findall(ATOM + "entry"):
            link_el = e.find(ATOM + "link")
            link = link_el.get("href") if link_el is not None else ""
            summ = _text(e.find(ATOM + "summary")) or _text(e.find(ATOM + "content"))
            pubs = _text(e.find(ATOM + "updated")) or _text(e.find(ATOM + "published"))
            items.append(
                NewsItem(
                    title=_text(e.find(ATOM + "title")),
                    url=link or "",
                    source=src,
                    published=_parse_date(pubs, tz),
                    summary=_strip_html(summ),
                )
            )
    return items


def fetch_all(feeds: list[tuple[str, str]], tz: ZoneInfo) -> list[NewsItem]:
    """抓取并解析所有源；单个源失败不影响其它源。"""
    out: list[NewsItem] = []
    for name, url in feeds:
        try:
            items = parse_feed(_fetch(url), name, tz)
            for it in items:
                it.feed_url = url  # 标记来源 RSS，供分类专属源归属
            out.extend(items)
        except Exception as e:  # noqa: BLE001 — 抓取失败仅告警，不中断
            print(f"[warn] 抓取失败 {name} ({url}): {e}")
    return out
