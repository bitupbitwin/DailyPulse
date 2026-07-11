package com.infopulse.app.data

/**
 * 后端 JSON 响应模型（对应 backend/infopulse/api/schemas.py）。
 * 字段名用 @snake_case 与后端保持一致，Gson 直接映射。
 */

data class CategoryDto(
    val id: String = "",
    val name: String = "",
    val icon: String = "",
    val keywords: List<String> = emptyList(),
    val summary: String = "",
)

data class SourceDto(
    val tag: String = "",
    val title: String = "",
    val media: String = "",
    val date: String = "",
    val content: String = "",
    val extra: String = "",
    val url: String = "",
)

data class BriefingDto(
    val report_date: String = "",
    val weekday: String = "",
    val generated_at: String = "",
    val categories: List<CategoryDto> = emptyList(),
    val status: String = "",
    val content_markdown: String = "",
    val sources: List<SourceDto> = emptyList(),
)

data class RefreshRequestDto(val date: String? = null)

data class RefreshResponseDto(val task_id: String = "", val status: String = "")

data class TaskStatusDto(val task_id: String = "", val status: String = "", val error: String? = null)
