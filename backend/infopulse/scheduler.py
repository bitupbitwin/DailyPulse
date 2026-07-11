"""每日定时任务：凌晨自动生成前一天（T-1）的各分类简报，写入 SQLite。

对应开发说明书 §3.1「凌晨预生成、App 秒开」。使用 APScheduler 的 AsyncIOScheduler，
与 FastAPI 事件循环共存。若未安装 apscheduler 或 SCHEDULE_HOUR=-1，则安全跳过。
"""
from __future__ import annotations

from .settings import settings

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ImportError:  # 未装 apscheduler：不崩溃，只是没有定时能力
    AsyncIOScheduler = None  # type: ignore

_scheduler = None


async def _daily_job() -> None:
    """生成所有启用分类的 T-1 简报。单个分类失败不影响其它分类
    （generate_async 内部对每个分类单独 try/except，失败记为 failed 状态）。"""
    # 延迟导入，避免与 orchestrator 的循环依赖
    from .orchestrator import generate_async

    try:
        target, results = await generate_async(use_llm=True, use_search=True)
        ok = sum(1 for r in results if r.status == "ready")
        print(f"[scheduler] {target} 定时简报完成：{ok}/{len(results)} 个分类就绪")
    except Exception as exc:  # noqa: BLE001 — 定时任务不能因异常中断进程
        print(f"[scheduler] 定时生成失败：{exc}")


def start_scheduler() -> None:
    """在 FastAPI 启动时调用。"""
    global _scheduler
    if AsyncIOScheduler is None:
        print("[scheduler] 未安装 apscheduler，跳过定时任务（可 pip install apscheduler 开启）")
        return
    if settings.schedule_hour < 0:
        print("[scheduler] SCHEDULE_HOUR=-1，定时任务已关闭")
        return
    if _scheduler is not None:
        return
    try:
        _scheduler = AsyncIOScheduler(timezone=settings.timezone)
        _scheduler.add_job(
            _daily_job,
            trigger="cron",
            hour=settings.schedule_hour,
            minute=settings.schedule_minute,
            id="daily_briefing",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        _scheduler.start()
        print(f"[scheduler] 已启动：每日 {settings.schedule_hour:02d}:{settings.schedule_minute:02d} 生成 T-1 简报")
    except Exception as exc:  # noqa: BLE001 — 定时器初始化失败不应拖垮 API 启动
        print(f"[scheduler] 启动失败（API 仍可用，仅无定时）：{exc}")
        _scheduler = None


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
