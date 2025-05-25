from fastapi import APIRouter, Depends, Query
from typing import List
from app.services import OfficeService
from app.domain.models import Office
from app.api.dependencies import get_office_service

router = APIRouter(prefix="/office", tags=["office"])


@router.get("/", response_model=List[Office])
async def get_offices(
    return_components: bool = Query(False, description="Whether to return devices and their components"),
    office_service: OfficeService = Depends(get_office_service)
):
    return await office_service.get_all_offices(return_components)


@router.get("/{office_id}", response_model=Office)
async def get_office(
    office_id: int,
    return_components: bool = Query(False, description="Whether to return devices and their components"),
    office_service: OfficeService = Depends(get_office_service)
):
    return await office_service.get_office_by_id(office_id, return_components)


@router.post("/", response_model=Office)
async def create_office(office: Office, office_service: OfficeService = Depends(get_office_service)):
    return await office_service.create_office(office)


@router.patch("/{office_id}", response_model=Office)
async def update_office(office_id: int, office: Office, office_service: OfficeService = Depends(get_office_service)):
    return await office_service.update_office(office_id, office)


@router.delete("/{office_id}", response_model=bool)
async def delete_office(office_id: int, office_service: OfficeService = Depends(get_office_service)):
    return await office_service.delete_office(office_id)
