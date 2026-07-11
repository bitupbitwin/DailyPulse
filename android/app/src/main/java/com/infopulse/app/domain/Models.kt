package com.infopulse.app.domain

/** 单条新闻 —— 对应开发说明书 §4.4 简报中的一条记录 */
data class NewsItem(
    val tag: String,      // 主体标签，如「DeepSeek · 深度求索」
    val title: String,    // 标题
    val media: String,    // 来源媒体
    val date: String,     // 发布日期（必须为目标日期）
    val content: String,  // 正文摘要
    val extra: String,    // 结构化要点（▸ ...）
)

/** 分类 —— 如「AI 大模型」 */
data class Category(
    val id: String,
    val name: String,
    val icon: String,
    val summary: String,
    val items: List<NewsItem>,
    val markdown: String = "",   // AI 提炼后的简报全文（Markdown）；mock 数据留空
    val status: String = "ready", // ready | empty | failed | running
)

/** 一次简报快照（某个目标日期、各分类） */
data class Briefing(
    val reportDate: String,
    val weekday: String,
    val generatedAt: String,
    val categories: List<Category>,
)
