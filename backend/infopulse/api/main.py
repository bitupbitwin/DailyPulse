from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import load_config
from ..db import init_db, sync_categories
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    _, categories = load_config()
    await sync_categories(categories)
    yield


app = FastAPI(title="InfoPulse API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
