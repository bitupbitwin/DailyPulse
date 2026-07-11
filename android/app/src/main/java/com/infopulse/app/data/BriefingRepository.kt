package com.infopulse.app.data

import com.infopulse.app.domain.Briefing
import com.infopulse.app.domain.Category
import com.infopulse.app.domain.NewsItem

/**
 * 数据仓库：把后端多个接口拼装成 UI 需要的 domain.Briefing。
 *
 * 后端 /categories 只给分类清单与摘要；每个分类的当日简报要单独取 /briefing，
 * 其中 content_markdown 是 AI 提炼全文、sources 是检索到的原始新闻。
 * 这里把 sources 映射成 UI 的 NewsItem 卡片，并把 markdown 一并带上（供详情/追问用）。
 */
class BriefingRepository(private val api: ApiService = ApiClient.service) {

    /** 拉取所有分类 + 各自最新简报，组装成一个 Briefing。 */
    suspend fun loadBriefing(): Briefing {
        val categories = api.getCategories()

        var reportDate = ""
        var weekday = ""
        var generatedAt = ""

        val domainCats = categories.map { cat ->
            val brief = runCatching { api.getBriefing(cat.id, null) }.getOrNull()
            if (brief != null && reportDate.isEmpty() && brief.status != "empty") {
                reportDate = brief.report_date
                weekday = brief.weekday
                generatedAt = brief.generated_at
            }
            Category(
                id = cat.id,
                name = cat.name,
                icon = cat.icon,
                summary = cat.summary.ifBlank { brief?.let { firstLine(it.content_markdown) } ?: "" },
                items = brief?.sources.orEmpty().map { it.toDomain() },
                markdown = brief?.content_markdown ?: "",
                status = brief?.status ?: "empty",
            )
        }

        return Briefing(
            reportDate = reportDate,
            weekday = weekday,
            generatedAt = generatedAt,
            categories = domainCats,
        )
    }

    /** 触发某分类重新生成，返回 task_id。 */
    suspend fun triggerRefresh(catId: String): String =
        api.refreshCategory(catId, RefreshRequestDto()).task_id

    /** 轮询任务状态直至结束（ready/failed），或超过 maxPolls 次。 */
    suspend fun pollUntilDone(taskId: String, maxPolls: Int = 60): String {
        var status = "pending"
        var polls = 0
        while (status == "pending" || status == "running") {
            if (polls++ >= maxPolls) break
            kotlinx.coroutines.delay(2000)
            status = runCatching { api.getTaskStatus(taskId).status }.getOrDefault("failed")
        }
        return status
    }

    private fun SourceDto.toDomain(): NewsItem = NewsItem(
        tag = tag.ifBlank { media },
        title = title,
        media = media,
        date = date,
        content = content,
        extra = extra,
    )

    private fun firstLine(markdown: String): String =
        markdown.lineSequence()
            .map { it.trim().trimStart('#', '=', '·', '|', '-', ' ') }
            .firstOrNull { it.isNotEmpty() && !it.startsWith("📅") }
            ?.take(60) ?: ""
}
