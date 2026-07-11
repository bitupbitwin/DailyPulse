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
        # 博查检索时间窗；留空则自动用目标日期（推荐）。可覆盖为 oneDay/oneWeek 等。
        self.bocha_freshness = os.environ.get("BOCHA_FRESHNESS", "")
        # 备用 LLM 网关（如硅基流动 SiliconFlow）——主 DeepSeek 失败时自动降级。
        self.fallback_base_url = os.environ.get("FALLBACK_BASE_URL", "")
        self.fallback_api_key = os.environ.get("FALLBACK_API_KEY", "")
        self.fallback_model = os.environ.get("FALLBACK_MODEL", "")
        self.timezone = os.environ.get("TIMEZONE", "Asia/Shanghai")
        self.max_items_per_category = int(os.environ.get("MAX_ITEMS_PER_CATEGORY", "25"))
        self.http_timeout = int(os.environ.get("HTTP_TIMEOUT", "20"))
        # 定时任务：每日几点生成 T-1 简报（0-23）；-1 表示关闭调度。
        self.schedule_hour = int(os.environ.get("SCHEDULE_HOUR", "6"))
        self.schedule_minute = int(os.environ.get("SCHEDULE_MINUTE", "0"))
        # API 允许的跨域来源；默认 * （开发期）。上架前用逗号分隔配置具体域名。
        self.cors_origins = [
            o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()
        ]
        # 可选：API 鉴权 token（Bearer）。留空表示不鉴权（MVP 默认）。
        self.api_token = os.environ.get("API_TOKEN", "")


settings = Settings()
