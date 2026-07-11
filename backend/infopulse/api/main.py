from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import load_config
from ..db import init_db, sync_categories
from ..scheduler import shutdown_scheduler, start_scheduler
from ..settings import settings
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    _, categories = load_config()
    await sync_categories(categories)
    start_scheduler()          # 每日定时生成 T-1 简报
    try:
        yield
    finally:
        shutdown_scheduler()


app = FastAPI(title="InfoPulse API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
