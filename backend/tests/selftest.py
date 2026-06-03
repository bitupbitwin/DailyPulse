"""离线自测：验证 RSS 解析 + 日期硬过滤 + 关键词归类（无需网络/无需 DeepSeek Key）。

运行：  cd backend && python -m tests.selftest
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

from infopulse import clean, rss
from infopulse.config import load_config

TZ = ZoneInfo("Asia/Shanghai")
TARGET = date(2026, 6, 2)


def main() -> None:
    sample = (Path(__file__).parent / "sample_feed.xml").read_bytes()
    items = rss.parse_feed(sample, "测试源", TZ)
    assert len(items) == 4, f"应解析出 4 条，实际 {len(items)}"

    # 日期硬过滤：剔除 5/31 的旧闻 → 剩 3 条
    dated = clean.filter_by_date(items, TARGET)
    assert len(dated) == 3, f"日期过滤后应剩 3 条，实际 {len(dated)}"

    _, categories = load_config()
    by_id = {c.id: c for c in categories}

    ai = clean.select_for_category(items, by_id["cat_ai"], TARGET, 25)
    assert len(ai) == 1 and "DeepSeek" in ai[0].title, f"AI 分类应命中 1 条 DeepSeek，实际 {[x.title for x in ai]}"

    ev = clean.select_for_category(items, by_id["cat_ev"], TARGET, 25)
    assert len(ev) == 1 and "比亚迪" in ev[0].title, f"车企分类应命中 1 条比亚迪，实际 {[x.title for x in ev]}"

    net = clean.select_for_category(items, by_id["cat_internet"], TARGET, 25)
    assert len(net) == 0, f"大厂分类应命中 0 条，实际 {[x.title for x in net]}"

    # HTML 已被清洗
    assert "<p>" not in ai[0].summary

    print("✅ 自测通过：")
    print(f"   - RSS 解析 4 条，日期过滤后 3 条（旧闻已剔除）")
    print(f"   - AI 大模型 命中：{ai[0].title}")
    print(f"   - 新能源车企 命中：{ev[0].title}")
    print(f"   - 互联网大厂 命中：0 条（天气新闻被关键词过滤）")


if __name__ == "__main__":
    main()
