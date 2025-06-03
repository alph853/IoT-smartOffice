from datetime import datetime, time
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class ScheduleType(Enum):
    LIGHTING = "lighting"
    FAN = "fan"

    class Config:
        use_enum_values = True


class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    class Config:
        use_enum_values = True


class LightingScheduleSetting(BaseModel):
    color: Tuple[Tuple[int, int, int], ...]  # RGB tuples for LED strips
    brightness: int = Field(default=100, ge=0, le=100)  # Brightness (0-100)

    class Config:
        use_enum_values = True


class FanScheduleSetting(BaseModel):
    state: bool  # Fan on/off
    speed: Optional[int] = Field(default=None, ge=0, le=100)  # Speed (0-100)

    class Config:
        use_enum_values = True


class Schedule(BaseModel):
    id: Optional[str] = None  # UUID string
    name: str
    actuator_id: int
    schedule_type: ScheduleType
    days_of_week: List[DayOfWeek]
    start_time: time  # Start time (hour:minute)
    end_time: time    # End time (hour:minute)
    setting: Dict[str, Any]  # Type-specific settings (LightingScheduleSetting or FanScheduleSetting)
    priority: int = Field(default=0, ge=0)  # Priority (higher wins conflicts)
    is_active: bool = Field(default=True)   # Enable/disable schedule
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            time: lambda v: v.strftime("%H:%M")
        }


class ScheduleCreate(BaseModel):
    name: str
    actuator_id: int
    schedule_type: ScheduleType
    days_of_week: List[DayOfWeek]
    start_time: time
    end_time: time
    setting: Dict[str, Any]
    priority: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)

    class Config:
        use_enum_values = True
        json_encoders = {
            time: lambda v: v.strftime("%H:%M")
        }


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    actuator_id: Optional[int] = None
    schedule_type: Optional[ScheduleType] = None
    days_of_week: Optional[List[DayOfWeek]] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    setting: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            time: lambda v: v.strftime("%H:%M")
        } 