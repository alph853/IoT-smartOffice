from fastapi import APIRouter, HTTPException, Response, status, Path
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Depends, Query


from app.domain.models import Device, DeviceRegistration
from app.services import DeviceService
from app.api.dependencies import get_device_service


router = APIRouter(prefix="/devices")


@router.get("/", response_model=List[Device])
async def get_devices(
    device_service: DeviceService = Depends(get_device_service),
):
    devices = await device_service.get_devices()
    return devices


@router.get("/{device_id}", response_model=Device)
async def get_device_by_id(
    device_id: str,
    device_service: DeviceService = Depends(get_device_service),
):
    device = await device_service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/", response_model=Device)
async def create_device(
    device: DeviceRegistration,
    device_service: DeviceService = Depends(get_device_service),
):
    device = await device_service.create_device(device)
    return device


@router.patch("/{device_id}", response_model=Device)
async def update_device(
    device_id: str,
    device: Device,
    device_service: DeviceService = Depends(get_device_service),
):
    device = await device_service.update_device(device_id, device)
    return device


@router.delete("/{device_id}", response_model=Device)
async def delete_device(
    device_id: str,
    device_service: DeviceService = Depends(get_device_service),
):
    device = await device_service.delete_device(device_id)
    return device

