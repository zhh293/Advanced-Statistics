from __future__ import annotations
from typing import Optional, List, Any
from pydantic import BaseModel


class DeptCreate(BaseModel):
    dept_name: str
    description: Optional[str] = None
    floor_no: Optional[int] = None


class DeptUpdate(BaseModel):
    dept_name: Optional[str] = None
    description: Optional[str] = None
    floor_no: Optional[int] = None


class RoomItem(BaseModel):
    room_id: int
    room_name: str
    room_no: str

    model_config = {"from_attributes": True}


class DoctorBrief(BaseModel):
    doctor_id: int
    real_name: str
    title: str
    specialty: Optional[str]

    model_config = {"from_attributes": True}


class DeptOut(BaseModel):
    dept_id: int
    dept_name: str
    description: Optional[str]
    floor_no: Optional[int]
    doctor_count: int

    model_config = {"from_attributes": True}


class DeptDetail(BaseModel):
    dept_id: int
    dept_name: str
    description: Optional[str]
    floor_no: Optional[int]
    rooms: List[RoomItem]
    doctors: List[DoctorBrief]
