from __future__ import annotations

import json
from datetime import date

from .models import Category, NewsItem

# 平台硬约束（用户不可覆盖）—— 对应开发说明书 §7.1
SYSTEM_PROMPT = """你是一个严谨的每日资讯提炼助手。你只能基于【素材】中提供的新闻进行提炼，禁止使用素材外的任何信息，禁止编造。

时间规则：
- 今日日期：{current_date}
- 目标日期：{target_date}
- 只保留发布日期 = 目标日期 的新闻；其余一律丢弃。
- 某主体/板块无符合条件的新闻：整块省略，不写任何占位文字。

内容规则：
- 每条必须是目标日期当天真实发生的具体事件，不得泛泛概括。
- 每条必须注明：来源媒体 + 发布日期（必须是目标日期）。
- 无法确认来源或日期的信息，直接跳过。
- 禁止“持续发力”“整体趋势”等空话。

输出规则：
- 严格按【输出格式】渲染。
- 全程中文。"""

# AI 大模型专用格式（用户自定义的简报样式）
AI_FORMAT = """════════════════════════════════
📅 AI 大模型动态简报
   报告日期：[目标日期]
   生成时间：[执行日期]
════════════════════════════════

⚠️ 本报告仅收录 [目标日期] 当日发布的新闻，无新闻的板块已自动省略。

---

（针对素材中出现的每一个主体/模型，有新闻才写一个板块，无则整块跳过；按下面模板组织。）

【主体名称 · 公司】
📰 [新闻标题]
   来源：XX媒体 | 日期：[目标日期]
   内容：具体发生了什么（2-3句，说清事件、数据、影响）
   ▸ 如涉及新模型：注明模型名称 + 参数量 + 性能对标
   ▸ 如涉及融资/合作：注明金额 + 合作方 + 应用场景
   ▸ 如涉及新功能：注明功能名 + 适用用户（免费/付费）+ 上线范围

════════════════════════════════
✅ 今日报告生成完毕（数据来源：[目标日期] 当日新闻）
════════════════════════════════"""

# 通用格式（新能源车企 / 互联网大厂等）
DEFAULT_FORMAT = """════════════════════════════════
📅 [分类名称] · 每日动态简报
   报告日期：[目标日期]
   生成时间：[执行日期]
════════════════════════════════

⚠️ 本报告仅收录 [目标日期] 当日发布的新闻，无新闻的主体已自动省略。

---

（针对素材中出现的每一个主体/公司，有新闻才写一个板块，无则整块跳过。）

【主体名称】
📰 [新闻标题]
   来源：XX媒体 | 日期：[目标日期]
   内容：具体发生了什么（2-3句，说清事件、数据、影响）
   ▸ 关键数据/动作：金额、规模、时间、对比等可量化信息

════════════════════════════════
✅ 今日报告生成完毕（数据来源：[目标日期] 当日新闻）
════════════════════════════════"""

FORMATS: dict[str, str] = {"cat_ai": AI_FORMAT}


def _format_for(cat: Category) -> str:
    return cat.output_format or FORMATS.get(cat.id) or DEFAULT_FORMAT


def build_messages(
    cat: Category, items: list[NewsItem], target: date, current: date
) -> list[dict]:
    """构建 system + user 两条消息；素材以 JSON 注入。"""
    fmt = (
        _format_for(cat)
        .replace("[分类名称]", cat.name)
        .replace("[目标日期]", target.isoformat())
        .replace("[执行日期]", current.isoformat())
    )
    system = SYSTEM_PROMPT.format(current_date=current.isoformat(), target_date=target.isoformat())
    material = [
        {
            "title": it.title,
            "media": it.source,
            "published_at": it.published.isoformat() if it.published else "",
            "summary": it.summary,
            "url": it.url,
        }
        for it in items
    ]
    user = (
        f"领域：{cat.name}\n\n"
        f"【输出格式】\n{fmt}\n\n"
        f"【素材】（共 {len(material)} 条，JSON）\n"
        + json.dumps({"items": material}, ensure_ascii=False, indent=2)
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
