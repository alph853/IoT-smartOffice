from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class MultimediaData(BaseModel):
    id: int | None = None
    filename: str | None = None
    image_data: str
    image_path: str | None = None
    image_embedding: List
    created_at: datetime = datetime.now()


class Image(BaseModel):
    filename: str
    image_data: str
    created_at: datetime

class MultimediaResponse(BaseModel):
    images: List[Image]