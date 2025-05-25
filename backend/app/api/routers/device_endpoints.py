from fastapi import APIRouter, HTTPException, Response, status, Path
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Depends, Query
import asyncpg

from app.domain.models import Device, DeviceRegistration, DeviceUpdate, Sensor, Actuator
from app.services import DeviceService
from app.api.dependencies import get_device_service


router = APIRouter(prefix="/devices")


@router.get("/", response_model=List[Device])
async def get_devices(
    return_components: bool = Query(False, description="Whether to return sensors and actuators"),
    device_service: DeviceService = Depends(get_device_service),
):
    devices = await device_service.get_devices(return_components=return_components)
    return devices


@router.get("/sensors", response_model=List[Sensor])
async def get_all_sensors(
    device_service: DeviceService = Depends(get_device_service),
):
    return await device_service.get_all_sensors()


@router.get("/actuators", response_model=List[Actuator])
async def get_all_actuators(
    device_service: DeviceService = Depends(get_device_service),
):
    return await device_service.get_all_actuators()


@router.get("/{device_id}", response_model=Device)
async def get_device_by_id(
    device_id: int,
    return_components: bool = Query(False, description="Whether to return sensors and actuators"),
    device_service: DeviceService = Depends(get_device_service),
):
    device = await device_service.get_device_by_id(device_id, return_components=return_components)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/", response_model=Device)
async def create_device(
    device: DeviceRegistration,
    device_service: DeviceService = Depends(get_device_service),
):
    """Only for CRUD testing. The actual device creation is done through gateway (device registration)."""
    try:
        device = await device_service.create_device(device)
    except asyncpg.UniqueViolationError as e:
        raise HTTPException(status_code=400, detail=f'Device may be already existed: {e}')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return device


@router.post("/connect", response_model=Device)
async def connect_device(
    device: DeviceRegistration,
    device_service: DeviceService = Depends(get_device_service),
):
    """API exposed for the gateway to call for device registration. Create a new device if none exists."""
    device = await device_service.connect_device(device)
    return device


@router.patch("/disable/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_device(
    device_id: int,
    device_service: DeviceService = Depends(get_device_service),
):
    if not await device_service.disable_device(device_id):
        raise HTTPException(status_code=404, detail="Device not found")


@router.patch("/enable/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def enable_device(
    device_id: int,
    device_service: DeviceService = Depends(get_device_service),
):
    if not await device_service.enable_device(device_id):
        raise HTTPException(status_code=404, detail="Device not found")


@router.patch("/{device_id}", response_model=Device)
async def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    device_service: DeviceService = Depends(get_device_service),
):
    device = await device_service.update_device(device_id, device_update)
    if not device:
        raise HTTPException(status_code=404, detail="Invalid update. Perhaps check your request body.")
    return device


@router.delete("/delete-all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_devices(
    device_service: DeviceService = Depends(get_device_service),
):
    if not await device_service.delete_all_devices():
        raise HTTPException(status_code=404, detail="Device not found")

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    device_service: DeviceService = Depends(get_device_service),
):
    if not await device_service.delete_device(device_id):
        raise HTTPException(status_code=404, detail="Device not found")
