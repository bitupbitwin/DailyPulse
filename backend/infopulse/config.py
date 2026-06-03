from __future__ import annotations

from pathlib import Path

import yaml

from .models import Category
from .settings import BASE_DIR


def load_config(path: Path | None = None) -> tuple[list[tuple[str, str]], list[Category]]:
    """读取 config/categories.yaml，返回 (feeds, categories)。"""
    path = path or (BASE_DIR / "config" / "categories.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    feeds: list[tuple[str, str]] = []
    for f in data.get("feeds", []) or []:
        url = (f.get("url") or "").strip()
        if url:
            feeds.append((f.get("name", url), url))

    categories: list[Category] = []
    for c in data.get("categories", []) or []:
        categories.append(
            Category(
                id=c["id"],
                name=c["name"],
                icon=c.get("icon", ""),
                keywords=[str(k) for k in c.get("keywords", [])],
                output_format=c.get("output_format"),
            )
        )
    return feeds, categories
