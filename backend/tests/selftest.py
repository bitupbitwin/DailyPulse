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

    # 扩展性：分类专属源（owners）——把"天气"那条所在的源指给一个无关键词命中的新类，
    # 它应被直接归入（验证不靠关键词也能纳入专属源新闻）。
    from infopulse.models import Category
    weather_item = next(it for it in items if "天气" in it.title)
    weather_item.feed_url = "https://feed.weather/rss"
    sports = Category(id="cat_sports", name="本地资讯", icon="📰", keywords=[],
                      feeds=[("天气源", "https://feed.weather/rss")])
    owners = {"https://feed.weather/rss": {"cat_sports"}}
    owned = clean.select_for_category(items, sports, TARGET, 25, owners)
    assert len(owned) == 1 and "天气" in owned[0].title, \
        f"专属源应直接归入 1 条，实际 {[x.title for x in owned]}"

    print("✅ 自测通过：")
    print(f"   - RSS 解析 4 条，日期过滤后 3 条（旧闻已剔除）")
    print(f"   - AI 大模型 命中：{ai[0].title}")
    print(f"   - 新能源车企 命中：{ev[0].title}")
    print(f"   - 互联网大厂 命中：0 条（天气新闻被关键词过滤）")
    print(f"   - 分类专属源：无关键词也能纳入专属源新闻（扩展性 OK）")


if __name__ == "__main__":
    main()
