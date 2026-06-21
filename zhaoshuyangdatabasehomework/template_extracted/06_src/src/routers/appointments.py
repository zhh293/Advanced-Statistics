from __future__ import annotations
from typing import Optional, List, Any
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (
    Users, Patient, Schedule, Appointment,
    Doctor, Department, Room, MedicalRecord,
)
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp, PagedData
from ..schemas.appointment import (
    AppointmentCreate, CancelIn,
    AppointmentOut, AppointmentDetail, TodayItem,
)

router = APIRouter(prefix="/appointments", tags=["预约"])


def _appt_out(a: Appointment, db: Session) -> AppointmentOut:
    s = db.get(Schedule, a.schedule_id)
    doctor = db.get(Doctor, s.doctor_id)
    dept = db.get(Department, doctor.dept_id)
    return AppointmentOut(
        appointment_id=a.appointment_id,
        doctor_name=doctor.real_name,
        dept_name=dept.dept_name,
        work_date=s.work_date.isoformat(),
        time_period=s.time_period,
        queue_no=a.queue_no,
        status=a.status,
        created_at=a.created_at.isoformat(),
    )


@router.post("", status_code=201)
def create_appointment(
    body: AppointmentCreate,
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
    if patient is None:
        raise AppError(40001, "患者档案不存在，请先完善个人信息", 400)
    schedule = db.get(Schedule, body.schedule_id)
    if schedule is None:
        raise AppError(40401, "排班不存在", 404)
    if schedule.status == "停诊":
        raise AppError(40903, "排班已停诊", 400)
    if schedule.status == "约满":
        raise AppError(40901, "该排班已约满", 400)
    existing = db.query(Appointment).filter(
        Appointment.patient_id == patient.patient_id,
        Appointment.schedule_id == body.schedule_id,
    ).first()
    if existing:
        raise AppError(40902, "您已预约过该排班", 409)

    queue_no = schedule.registered_count + 1
    appt = Appointment(
        patient_id=patient.patient_id,
        schedule_id=body.schedule_id,
        queue_no=queue_no,
        status="待就诊",
    )
    db.add(appt)
    schedule.registered_count += 1
    if schedule.registered_count >= schedule.max_patients:
        schedule.status = "约满"
    db.commit()
    db.refresh(appt)

    doctor = db.get(Doctor, schedule.doctor_id)
    dept = db.get(Department, doctor.dept_id)
    room = db.get(Room, schedule.room_id)
    return Resp.created(
        data={
            "appointment_id": appt.appointment_id,
            "schedule_id": schedule.schedule_id,
            "doctor_name": doctor.real_name,
            "dept_name": dept.dept_name,
            "work_date": schedule.work_date.isoformat(),
            "time_period": schedule.time_period,
            "room_no": room.room_no,
            "queue_no": appt.queue_no,
            "status": appt.status,
            "created_at": appt.created_at.isoformat(),
        },
        message="预约成功",
    )


@router.get("/today")
def today_list(
    date_str: Optional[str] = None,
    time_period: Optional[str] = None,
    current_user: Users = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if doctor is None:
        raise AppError(40401, "医生档案不存在", 404)
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    q = (
        db.query(Appointment)
        .join(Schedule)
        .filter(
            Schedule.doctor_id == doctor.doctor_id,
            Schedule.work_date == target_date,
        )
    )
    if time_period:
        q = q.filter(Schedule.time_period == time_period)
    appts = q.order_by(Appointment.queue_no).all()

    def _age(p: Patient) -> int:
        if p.birth_date:
            today = date.today()
            return today.year - p.birth_date.year - (
                (today.month, today.day) < (p.birth_date.month, p.birth_date.day)
            )
        return 0

    result = [
        TodayItem(
            appointment_id=a.appointment_id,
            queue_no=a.queue_no,
            patient_name=db.get(Patient, a.patient_id).real_name,
            gender=db.get(Patient, a.patient_id).gender,
            age=_age(db.get(Patient, a.patient_id)),
            status=a.status,
            has_record=a.medical_record is not None,
        )
        for a in appts
    ]
    return Resp.ok(data={"list": [i.model_dump() for i in result], "total": len(result)})


@router.get("")
def list_appointments(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
    if patient is None:
        raise AppError(40001, "患者档案不存在", 400)
    q = db.query(Appointment).filter(Appointment.patient_id == patient.patient_id)
    if status:
        q = q.filter(Appointment.status == status)
    total = q.count()
    appts = (
        q.order_by(Appointment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return Resp.ok(data=PagedData(
        list=[_appt_out(a, db) for a in appts],
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: int,
    current_user: Users = Depends(require_role("patient", "admin")),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, appointment_id)
    if appt is None:
        raise AppError(40401, "预约不存在", 404)
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
        if patient is None or appt.patient_id != patient.patient_id:
            raise AppError(40302, "无权操作他人预约", 403)
    s = db.get(Schedule, appt.schedule_id)
    doctor = db.get(Doctor, s.doctor_id)
    dept = db.get(Department, doctor.dept_id)
    room = db.get(Room, s.room_id)
    p = db.get(Patient, appt.patient_id)
    return Resp.ok(data=AppointmentDetail(
        appointment_id=appt.appointment_id,
        patient_name=p.real_name,
        doctor_name=doctor.real_name,
        dept_name=dept.dept_name,
        room_no=room.room_no,
        work_date=s.work_date.isoformat(),
        time_period=s.time_period,
        queue_no=appt.queue_no,
        status=appt.status,
        created_at=appt.created_at.isoformat(),
        cancel_reason=appt.cancel_reason,
    ))


@router.put("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    body: CancelIn,
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    appt = db.get(Appointment, appointment_id)
    if appt is None:
        raise AppError(40401, "预约不存在", 404)
    patient = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
    if patient is None or appt.patient_id != patient.patient_id:
        raise AppError(40301, "无权操作他人预约", 403)
    if appt.status == "已就诊":
        raise AppError(40001, "该预约已就诊，无法取消", 400)
    if appt.status == "已取消":
        raise AppError(40002, "该预约已取消", 400)
    appt.status = "已取消"
    appt.cancel_reason = body.cancel_reason
    schedule = db.get(Schedule, appt.schedule_id)
    schedule.registered_count = max(0, schedule.registered_count - 1)
    if schedule.status == "约满" and schedule.registered_count < schedule.max_patients:
        schedule.status = "正常"
    db.commit()
    return Resp.ok(data=None, message="预约已取消")
