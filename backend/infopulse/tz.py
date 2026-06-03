"""时区工具：优先用 zoneinfo（需系统 tzdb 或 tzdata 包），
失败时回退到内置固定偏移，保证在 Windows 上无 tzdata 也能运行。

中国（Asia/Shanghai）自 1991 年起无夏令时，固定 UTC+8 完全正确。
"""
from __future__ import annotations

from datetime import timedelta, timezone, tzinfo

try:
    from zoneinfo import ZoneInfo
except ImportError:  # 理论上 3.9+ 都有；保险起见
    ZoneInfo = None  # type: ignore

_FIXED: dict[str, tzinfo] = {
    "UTC": timezone.utc,
    "Asia/Shanghai": timezone(timedelta(hours=8)),
    "Asia/Hong_Kong": timezone(timedelta(hours=8)),
    "Asia/Taipei": timezone(timedelta(hours=8)),
}


def get_tz(name: str) -> tzinfo:
    if ZoneInfo is not None:
        try:
            return ZoneInfo(name)
        except Exception:  # noqa: BLE001 — 缺 tzdata 时回退
            pass
    return _FIXED.get(name, _FIXED["Asia/Shanghai"])


UTC: tzinfo = get_tz("UTC")
