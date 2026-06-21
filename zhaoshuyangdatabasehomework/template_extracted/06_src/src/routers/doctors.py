from __future__ import annotations
from typing import Optional, List, Any
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users, Doctor, Department, Schedule, Appointment
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp, PagedData
from ..schemas.doctor import DoctorOut, DoctorDetail, DoctorMe, ScheduleBrief

router = APIRouter(prefix="/doctors", tags=["医生"])


def _build_detail(d: Doctor, db: Session) -> DoctorDetail:
    dept = db.get(Department, d.dept_id)
    return DoctorDetail(
        doctor_id=d.doctor_id,
        real_name=d.real_name,
        dept_id=d.dept_id,
        dept_name=dept.dept_name,
        title=d.title,
        specialty=d.specialty,
        intro=d.intro,
        is_active=d.is_active,
    )


@router.get("/me")
def doctor_me(
    current_user: Users = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if doctor is None:
        raise AppError(40401, "医生档案不存在", 404)
    detail = _build_detail(doctor, db)
    today = date.today()
    today_count = (
        db.query(Appointment)
        .join(Schedule)
        .filter(
            Schedule.doctor_id == doctor.doctor_id,
            Schedule.work_date == today,
        )
        .count()
    )
    week_end = today + timedelta(days=6)
    week_schedules = (
        db.query(Schedule)
        .filter(
            Schedule.doctor_id == doctor.doctor_id,
            Schedule.work_date >= today,
            Schedule.work_date <= week_end,
        )
        .all()
    )
    return Resp.ok(data=DoctorMe(
        **detail.model_dump(),
        today_appointments=today_count,
        schedules_this_week=[
            ScheduleBrief(
                schedule_id=s.schedule_id,
                work_date=s.work_date.isoformat(),
                time_period=s.time_period,
                registered_count=s.registered_count,
                max_patients=s.max_patients,
                status=s.status,
            )
            for s in week_schedules
        ],
    ))


@router.get("")
def list_doctors(
    dept_id: Optional[int] = None,
    title: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    q = db.query(Doctor).filter(Doctor.is_active == True)
    if dept_id:
        q = q.filter(Doctor.dept_id == dept_id)
    if title:
        q = q.filter(Doctor.title == title)
    if keyword:
        q = q.filter(
            or_(Doctor.real_name.contains(keyword), Doctor.specialty.contains(keyword))
        )
    total = q.count()
    doctors = q.offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for d in doctors:
        dept = db.get(Department, d.dept_id)
        result.append(DoctorOut(
            doctor_id=d.doctor_id,
            real_name=d.real_name,
            dept_name=dept.dept_name,
            title=d.title,
            specialty=d.specialty,
            is_active=d.is_active,
        ))
    return Resp.ok(data=PagedData(list=result, total=total, page=page, page_size=page_size))


@router.get("/{doctor_id}")
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise AppError(40401, "医生不存在", 404)
    return Resp.ok(data=_build_detail(doctor, db))
