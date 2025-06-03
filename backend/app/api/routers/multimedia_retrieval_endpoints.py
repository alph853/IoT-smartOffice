from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from app.domain.models import MultimediaData, MultimediaResponse
from app.services.multimedia_service import MultimediaService
from app.api.dependencies import get_multimedia_service

router = APIRouter(prefix="/multimedia", tags=["multimedia"])


@router.post("/images")
async def save_multimedia_data(
    multimedia_request: MultimediaData,
    multimedia_service: MultimediaService = Depends(get_multimedia_service)
):
    """Save multimedia data with actual image storage"""
    try:
        await multimedia_service.save_multimedia_data(multimedia_request)
        return {"message": "Multimedia data saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=MultimediaResponse)
async def get_multimedia_images(
    query: str = Query(default="", description="Optional search query for tags"),
    k: int = Query(default=10, description="Number of results to return"),
    multimedia_service: MultimediaService = Depends(get_multimedia_service)
):
    """Get multimedia images with actual image data"""
    try:
        results = await multimedia_service.get_multimedia_list(query, k)
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





