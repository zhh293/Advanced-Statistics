from __future__ import annotations
from typing import Optional, List, Any
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Schedule, Doctor, Department, Room
from ..exceptions import AppError
from ..schemas.common import Resp
from ..schemas.schedule import ScheduleOut

router = APIRouter(prefix="/schedules", tags=["排班"])


def _build_out(s: Schedule, db: Session) -> ScheduleOut:
    doctor = db.get(Doctor, s.doctor_id)
    dept = db.get(Department, doctor.dept_id)
    room = db.get(Room, s.room_id)
    return ScheduleOut(
        schedule_id=s.schedule_id,
        doctor_id=s.doctor_id,
        doctor_name=doctor.real_name,
        title=doctor.title,
        dept_name=dept.dept_name,
        room_no=room.room_no,
        work_date=s.work_date.isoformat(),
        time_period=s.time_period,
        max_patients=s.max_patients,
        registered_count=s.registered_count,
        remaining=s.max_patients - s.registered_count,
        status=s.status,
    )


@router.get("")
def list_schedules(
    dept_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    date_str: Optional[str] = None,
    time_period: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Schedule).filter(Schedule.status != "停诊")
    if doctor_id:
        q = q.filter(Schedule.doctor_id == doctor_id)
    if time_period:
        q = q.filter(Schedule.time_period == time_period)
    if date_str:
        q = q.filter(Schedule.work_date == date.fromisoformat(date_str))
    else:
        today = date.today()
        q = q.filter(
            Schedule.work_date >= today,
            Schedule.work_date <= today + timedelta(days=6),
        )
    if dept_id:
        doctor_ids = [
            d.doctor_id
            for d in db.query(Doctor).filter(Doctor.dept_id == dept_id).all()
        ]
        q = q.filter(Schedule.doctor_id.in_(doctor_ids))
    schedules = q.order_by(Schedule.work_date, Schedule.time_period).all()
    return Resp.ok(data=[_build_out(s, db) for s in schedules])


@router.get("/{schedule_id}")
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    s = db.get(Schedule, schedule_id)
    if s is None:
        raise AppError(40401, "排班不存在", 404)
    return Resp.ok(data=_build_out(s, db))
