from __future__ import annotations

import sys


def ensure_utf8_stdout() -> None:
    """让 stdout/stderr 用 UTF-8 输出，避免 Windows 默认 GBK 控制台在打印 emoji
    （如 ✅ 📅 🤖）时抛 UnicodeEncodeError。

    命令行入口调用一次即可；对已重定向到文件的情况也安全（reconfigure 存在才调用）。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass
