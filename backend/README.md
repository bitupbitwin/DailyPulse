# 资讯脉搏 后端 · 每日简报生成（RSS 免费源 + DeepSeek 提炼）

每天早晨运行一次，自动：抓取 RSS → 只保留「昨天」发布的新闻 → 按分类关键词归类 → 调用 **你自己的 DeepSeek** 提炼成简报。

- **零翻墙**：RSS 源与 DeepSeek 均国内直连。
- **几乎零依赖**：除 `PyYAML` 外全部用 Python 标准库（RSS 解析、HTTP、日期处理都没用第三方库）。
- **省钱可控**：搜索走免费 RSS；DeepSeek 按你 key 的 token 计费（每天几分钱量级）。

## 一、准备（一次性）

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # 可选，但推荐
pip install -r requirements.txt                      # 只装 PyYAML

cp .env.example .env
# 编辑 .env，把 DEEPSEEK_API_KEY 改成你自己的 key（platform.deepseek.com 申请）
```

> **Windows（CMD）** 用 `copy` 代替 `cp`，用 `notepad` 编辑：
> ```cmd
> pip install -r requirements.txt
> copy .env.example .env
> notepad .env
> ```
> 提示：先跑 `--no-llm`（下方）不需要配 key，可直接验证抓取效果。

## 二、每天早晨运行

```bash
python -m infopulse.generate            # 生成"昨天"的简报，调用 DeepSeek 提炼
```

- 控制台会直接打印每个分类的简报；
- 同时保存到 `output/` 目录：每个分类一个 `日期_分类id.md`，外加一个汇总 `日期_all.md`。

### 不花钱先试（强烈建议第一次这样跑）
```bash
python -m infopulse.generate --no-llm   # 只抓 RSS 原文、不调用模型，验证抓取与分类是否正常
```

### 指定日期 / 输出目录
```bash
python -m infopulse.generate --date 2026-06-02
python -m infopulse.generate --out /path/to/dir
```

## 三、自测（离线，不需要 key 和网络）
```bash
python -m tests.selftest
```
验证 RSS 解析、日期硬过滤、关键词归类是否正确。

## 四、改配置

编辑 `config/categories.yaml`：
- `feeds`：抓哪些 RSS 源（默认 IT之家、少数派，都是国内原生 RSS）。
- `categories`：分哪些类、每类的 `keywords`（命中标题/摘要即归入该类）。

> **关于 RSS 源**：很多国内媒体没有官方 RSS。默认两个源是确认有原生 RSS 的。想要更全（如 36氪、机器之心、各车企/大厂官博），推荐自建 [RSSHub](https://docs.rsshub.app/)，再把生成的路由 URL 填进 `feeds`。

## 五、工作原理（对应开发说明书）

```
RSS 抓取(rss.py) → 日期硬过滤+关键词归类+去重(clean.py)
   → 构建 Prompt(prompts.py, 系统硬约束+输出格式+素材JSON)
   → DeepSeek 提炼(deepseek.py) → 落地 Markdown(generate.py)
```

**日期准确性三道防线**：① RSS 只取最近条目；② 代码层 `clean.filter_by_date` 硬过滤掉非目标日期；③ Prompt 再次约束「非目标日期一律跳过、禁止编造」。

## 目录
```
backend/
├── config/categories.yaml      # 分类 + RSS 源（改这里即可）
├── infopulse/
│   ├── settings.py             # 读取 .env / 环境变量
│   ├── config.py               # 加载 yaml
│   ├── models.py               # NewsItem / Category / CategoryResult
│   ├── rss.py                  # 抓取 + 解析 RSS/Atom（标准库）
│   ├── clean.py                # 日期过滤 / 关键词归类 / 去重
│   ├── prompts.py              # 系统提示词 + 输出格式模板
│   ├── deepseek.py             # DeepSeek API 客户端（标准库 urllib）
│   ├── orchestrator.py         # 串联全流程
│   └── generate.py             # 命令行入口
├── tests/                      # 离线自测 + 样例数据
├── .env.example                # 配置模板（复制为 .env 填 key）
└── requirements.txt            # 仅 PyYAML
```

## 备注
- `.env`（含你的 key）和 `output/`（生成内容）都已在 `.gitignore` 中，不会被提交。
- 下一步可做：把生成结果用一个小型 FastAPI 服务暴露成接口，让 Android App 从 mock 切换到真实数据。
