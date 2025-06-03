package com.example.iot.domain.repositories

import ImageResponse
import retrofit2.http.GET
import retrofit2.http.Query

interface ImageRepository {
    @GET("multimedia/")
    suspend fun getImages(): ImageResponse

    @GET("multimedia/")
    suspend fun searchImages(@Query("query") query: String): ImageResponse
} 