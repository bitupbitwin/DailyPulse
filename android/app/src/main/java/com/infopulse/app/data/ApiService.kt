package com.infopulse.app.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

/** 后端 REST 接口（对应 backend/infopulse/api/routes.py，前缀 /api/v1）。 */
interface ApiService {
    @GET("api/v1/categories")
    suspend fun getCategories(): List<CategoryDto>

    @GET("api/v1/categories/{catId}/briefing")
    suspend fun getBriefing(
        @Path("catId") catId: String,
        @Query("date") date: String? = null,
    ): BriefingDto

    @POST("api/v1/categories/{catId}/refresh")
    suspend fun refreshCategory(
        @Path("catId") catId: String,
        @Body request: RefreshRequestDto,
    ): RefreshResponseDto

    @GET("api/v1/tasks/{taskId}")
    suspend fun getTaskStatus(@Path("taskId") taskId: String): TaskStatusDto
}
