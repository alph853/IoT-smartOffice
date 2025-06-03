from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime

from gateway.src.services.ai_service import AIMultimediaService

router = APIRouter(prefix="/multimedia", tags=["multimedia"])

# Global reference to AI service - this should be injected properly
_ai_service: AIMultimediaService = None


def set_ai_service(ai_service: AIMultimediaService):
    """Set the AI service instance"""
    global _ai_service
    _ai_service = ai_service


@router.get("/search")
async def search_images(
    query: str = Query(..., description="Search query text"),
    search_type: str = Query(default="hybrid", description="Search type: 'tag', 'nl', or 'hybrid'"),
    k: int = Query(default=10, ge=1, le=50, description="Number of results to return")
) -> Dict[str, Any]:
    """Search for images using natural language or tag queries"""
    
    if not _ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        results = await _ai_service.search_images(query, search_type, k)
        
        return {
            "query": query,
            "search_type": search_type,
            "total_results": len(results.get("results", [])),
            "results": results.get("results", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching images: {str(e)}")


@router.get("/status")
async def get_camera_status() -> Dict[str, Any]:
    """Get current status of the camera and AI processing"""
    
    if not _ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        status = _ai_service.get_camera_status()
        return {
            "status": "active",
            "camera_info": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.post("/settings")
async def update_camera_settings(
    polling_interval: float = Query(None, ge=1.0, le=300.0, description="Polling interval in seconds"),
    similarity_threshold: int = Query(None, ge=1, le=64, description="Image similarity threshold")
) -> Dict[str, Any]:
    """Update camera monitoring settings"""
    
    if not _ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        _ai_service.update_settings(
            polling_interval=polling_interval,
            similarity_threshold=similarity_threshold
        )
        
        updated_status = _ai_service.get_camera_status()
        
        return {
            "message": "Settings updated successfully",
            "current_settings": {
                "polling_interval": updated_status["polling_interval"],
                "similarity_threshold": updated_status["similarity_threshold"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")


@router.get("/images/metadata")
async def get_images_metadata(
    limit: int = Query(default=50, ge=1, le=200, description="Number of recent images to return")
) -> Dict[str, Any]:
    """Get metadata for recent processed images"""
    
    if not _ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        # Access the internal metadata - in production, this should be more controlled
        if hasattr(_ai_service, 'image_metadata'):
            metadata_items = list(_ai_service.image_metadata.values())
            
            # Sort by timestamp and limit
            sorted_metadata = sorted(
                metadata_items, 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )[:limit]
            
            return {
                "total_images": len(metadata_items),
                "returned_count": len(sorted_metadata),
                "images": sorted_metadata,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "total_images": 0,
                "returned_count": 0,
                "images": [],
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting images metadata: {str(e)}") 