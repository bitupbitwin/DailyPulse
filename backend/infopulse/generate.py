"""命令行入口：每天早晨运行一次，生成各分类的每日简报。

用法示例：
  python -m infopulse.generate                 # 生成"昨天"的简报（调用 DeepSeek）
  python -m infopulse.generate --no-llm        # 只抓 RSS 原文、不花钱调模型（调试）
  python -m infopulse.generate --date 2026-06-02
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .orchestrator import generate
from .settings import BASE_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="资讯脉搏 · 每日简报生成（RSS + DeepSeek）")
    parser.add_argument("--date", help="目标日期 YYYY-MM-DD（默认昨天）")
    parser.add_argument("--no-llm", action="store_true",
                        help="不调用 DeepSeek，仅按 RSS 原文组装（省钱/调试）")
    parser.add_argument("--out", default=str(BASE_DIR / "output"), help="输出目录")
    args = parser.parse_args()

    target = date.fromisoformat(args.date) if args.date else None
    target, results = generate(target_date=target, use_llm=not args.no_llm)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n📅 目标日期：{target}（共 {len(results)} 个分类）\n" + "=" * 40)
    combined: list[str] = []
    for r in results:
        head = f"{r.category.icon} {r.category.name}"
        if r.status == "empty":
            print(f"—— {head}：今日无符合条件的新闻，已省略")
            continue
        if r.status == "failed":
            print(f"!! {head}：生成失败 —— {r.error}")
            continue

        fn = outdir / f"{target}_{r.category.id}.md"
        fn.write_text(r.markdown, encoding="utf-8")
        print(f"\n== {head}（{len(r.items)} 条）→ {fn}\n")
        print(r.markdown)
        combined.append(f"\n\n# {head}\n\n{r.markdown}")

    if combined:
        all_fn = outdir / f"{target}_all.md"
        all_fn.write_text(
            f"# 资讯脉搏 · {target} 每日简报\n" + "".join(combined), encoding="utf-8"
        )
        print(f"\n汇总已保存：{all_fn}")


if __name__ == "__main__":
    main()
