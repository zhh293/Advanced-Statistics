from __future__ import annotations
from typing import Optional, List, Any
from pydantic import BaseModel


class DoctorOut(BaseModel):
    doctor_id: int
    real_name: str
    dept_name: str
    title: str
    specialty: Optional[str]
    is_active: bool


class DoctorDetail(BaseModel):
    doctor_id: int
    real_name: str
    dept_id: int
    dept_name: str
    title: str
    specialty: Optional[str]
    intro: Optional[str]
    is_active: bool


class ScheduleBrief(BaseModel):
    schedule_id: int
    work_date: str
    time_period: str
    registered_count: int
    max_patients: int
    status: str


class DoctorMe(DoctorDetail):
    today_appointments: int
    schedules_this_week: List[ScheduleBrief]
