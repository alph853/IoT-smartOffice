from fastapi import APIRouter

from app.domain.models.control import ControlCommand


router = APIRouter(prefix="/control", tags=["control"])


@router.post("/command")
async def create_control_command(command: ControlCommand):
    pass

