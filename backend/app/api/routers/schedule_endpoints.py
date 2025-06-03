from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from typing import List, Optional

from app.domain.models import Schedule, ScheduleCreate, ScheduleUpdate, ScheduleType
from app.services import ScheduleService
from app.api.dependencies import get_schedule_service


router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/", response_model=List[Schedule])
async def get_schedules(
    schedule_type: Optional[ScheduleType] = Query(None, description="Filter by schedule type"),
    active_only: bool = Query(False, description="Return only active schedules"),
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all schedules with optional filters"""
    try:
        if active_only:
            return await schedule_service.get_active_schedules()
        elif schedule_type:
            return await schedule_service.get_schedules_by_type(schedule_type)
        else:
            return await schedule_service.get_all_schedules()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schedules: {str(e)}")


@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule_by_id(
    schedule_id: str = Path(..., description="Schedule ID"),
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get a specific schedule by ID"""
    schedule = await schedule_service.get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/", response_model=Schedule, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Create a new schedule"""
    try:
        return await schedule_service.create_schedule(schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")


@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: str = Path(..., description="Schedule ID"),
    schedule_update: ScheduleUpdate = ...,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Update an existing schedule"""
    try:
        schedule = await schedule_service.update_schedule(schedule_id, schedule_update)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str = Path(..., description="Schedule ID"),
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Delete a schedule"""
    try:
        success = await schedule_service.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule: {str(e)}")


@router.get("/actuators/{actuator_id}/schedules", response_model=List[Schedule])
async def get_schedules_by_actuator(
    actuator_id: int = Path(..., description="Actuator ID"),
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all schedules for a specific actuator"""
    try:
        return await schedule_service.get_schedules_by_actuator_id(actuator_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schedules for actuator: {str(e)}")


# Convenience endpoints for specific schedule types
@router.get("/lighting/", response_model=List[Schedule])
async def get_lighting_schedules(
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all lighting schedules"""
    return await schedule_service.get_schedules_by_type(ScheduleType.LIGHTING)


@router.get("/fan/", response_model=List[Schedule])
async def get_fan_schedules(
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all fan schedules"""
    return await schedule_service.get_schedules_by_type(ScheduleType.FAN)
