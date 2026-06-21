from __future__ import annotations
from typing import Optional, List, Any
from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    schedule_id: int


class CancelIn(BaseModel):
    cancel_reason: Optional[str] = None


class AppointmentOut(BaseModel):
    appointment_id: int
    doctor_name: str
    dept_name: str
    work_date: str
    time_period: str
    queue_no: int
    status: str
    created_at: str


class AppointmentDetail(AppointmentOut):
    patient_name: str
    room_no: str
    cancel_reason: Optional[str]


class TodayItem(BaseModel):
    appointment_id: int
    queue_no: int
    patient_name: str
    gender: str
    age: int
    status: str
    has_record: bool
