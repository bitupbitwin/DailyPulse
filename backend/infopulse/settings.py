from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env(path: Path | None = None) -> None:
    """极简 .env 加载器（无需第三方依赖）。只设置尚未存在的环境变量。"""
    path = path or (BASE_DIR / ".env")
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


class Settings:
    def __init__(self) -> None:
        load_env()
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.deepseek_base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.deepseek_model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
        self.bocha_api_key = os.environ.get("BOCHA_API_KEY", "")
        self.bocha_base_url = os.environ.get("BOCHA_BASE_URL", "https://api.bochaai.com/v1")
        self.timezone = os.environ.get("TIMEZONE", "Asia/Shanghai")
        self.max_items_per_category = int(os.environ.get("MAX_ITEMS_PER_CATEGORY", "25"))
        self.http_timeout = int(os.environ.get("HTTP_TIMEOUT", "20"))


settings = Settings()
