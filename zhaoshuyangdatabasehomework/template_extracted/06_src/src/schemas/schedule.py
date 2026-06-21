from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    doctor_id: int
    room_id: int
    work_date: date
    time_period: str
    max_patients: int = 20


class ScheduleStatusUpdate(BaseModel):
    status: str


class ScheduleOut(BaseModel):
    schedule_id: int
    doctor_id: int
    doctor_name: str
    title: str
    dept_name: str
    room_no: str
    work_date: str
    time_period: str
    max_patients: int
    registered_count: int
    remaining: int
    status: str
