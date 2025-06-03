data class ImageResponse(
    val images: List<Image>
)

data class Image(
    val filename: String,
    val image_data: String,
    val created_at: String
)