package com.infopulse.app.data

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Retrofit 单例。
 * BASE_URL 用 10.0.2.2 —— Android 模拟器访问「宿主机 localhost」的特殊地址；
 * 真机调试时改成后端所在机器的局域网 IP（如 http://192.168.1.10:8000/）。
 * readTimeout 给足 120s，因为触发生成时后端要跑搜索 + DeepSeek。
 */
object ApiClient {
    private const val BASE_URL = "http://10.0.2.2:8000/"

    val service: ApiService by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .build()

        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
