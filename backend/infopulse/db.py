from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import aiosqlite

from .models import Category, CategoryResult, NewsItem
from .settings import BASE_DIR

DB_PATH = BASE_DIR / "data" / "infopulse.db"

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS category (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT NOT NULL,
    keywords TEXT NOT NULL,
    output_format TEXT,
    feeds TEXT NOT NULL DEFAULT '[]',
    sort_order INTEGER DEFAULT 0,
    is_enabled INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS briefing_report (
    id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL,
    report_date TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    content_markdown TEXT DEFAULT '',
    model TEXT DEFAULT '',
    token_prompt INTEGER DEFAULT 0,
    token_completion INTEGER DEFAULT 0,
    error TEXT,
    sources_json TEXT DEFAULT '[]',
    UNIQUE(category_id, report_date),
    FOREIGN KEY (category_id) REFERENCES category(id)
);
"""


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()


async def sync_categories(categories: list[Category]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        for idx, cat in enumerate(categories):
            await db.execute(
                """
                INSERT INTO category (
                    id, name, icon, keywords, output_format, feeds,
                    sort_order, is_enabled, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    icon=excluded.icon,
                    keywords=excluded.keywords,
                    output_format=excluded.output_format,
                    feeds=excluded.feeds,
                    sort_order=excluded.sort_order,
                    updated_at=excluded.updated_at
                """,
                (
                    cat.id,
                    cat.name,
                    cat.icon,
                    json.dumps(cat.keywords, ensure_ascii=False),
                    cat.output_format,
                    json.dumps(cat.feeds, ensure_ascii=False),
                    idx,
                    now,
                    now,
                ),
            )
        await db.commit()


async def save_briefing(
    result: CategoryResult,
    report_date: str,
    generated_at: str,
    model: str = "",
) -> None:
    await init_db()
    sources = [_item_to_source(item) for item in result.items]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO briefing_report (
                id, category_id, report_date, generated_at, status,
                content_markdown, model, error, sources_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(category_id, report_date) DO UPDATE SET
                id=excluded.id,
                generated_at=excluded.generated_at,
                status=excluded.status,
                content_markdown=excluded.content_markdown,
                model=excluded.model,
                error=excluded.error,
                sources_json=excluded.sources_json
            """,
            (
                f"{result.category.id}_{report_date}",
                result.category.id,
                report_date,
                generated_at,
                result.status,
                result.markdown,
                model,
                result.error,
                json.dumps(sources, ensure_ascii=False),
            ),
        )
        await db.commit()


async def get_briefing(category_id: str, report_date: str) -> dict[str, Any] | None:
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT * FROM briefing_report
            WHERE category_id = ? AND report_date = ?
            """,
            (category_id, report_date),
        )
        row = await cur.fetchone()
    return _row_to_dict(row)


async def get_latest_briefing(category_id: str, limit: int = 1) -> list[dict[str, Any]]:
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT * FROM briefing_report
            WHERE category_id = ?
            ORDER BY report_date DESC, generated_at DESC
            LIMIT ?
            """,
            (category_id, limit),
        )
        rows = await cur.fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def _row_to_dict(row: aiosqlite.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    data["sources"] = json.loads(data.pop("sources_json") or "[]")
    return data


def _item_to_source(item: NewsItem) -> dict[str, str]:
    return {
        "title": item.title,
        "media": item.source,
        "url": item.url,
        "published_at": item.published.isoformat() if item.published else "",
        "summary": item.summary,
    }
