from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users, Patient, Doctor, Department, Appointment, Schedule, MedicalRecord
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp
from ..schemas.medical_record import RecordCreate, RecordUpdate, RecordOut
from ..schemas.prescription import PrescriptionOut, DetailOut

router = APIRouter(prefix="/medical-records", tags=["病历"])


def _build_record_out(r: MedicalRecord, db: Session) -> RecordOut:
    patient = db.get(Patient, r.patient_id)
    doctor = db.get(Doctor, r.doctor_id)
    dept = db.get(Department, doctor.dept_id)
    presc_out = None
    if r.prescription:
        p = r.prescription
        details = [
            DetailOut(
                detail_id=d.detail_id,
                medicine_name=d.medicine.medicine_name,
                specification=d.medicine.specification,
                quantity=d.quantity,
                dosage=d.dosage,
                days=d.days,
                subtotal=d.subtotal,
            )
            for d in p.details
        ]
        presc_out = PrescriptionOut(
            prescription_id=p.prescription_id,
            record_id=p.record_id,
            total_price=p.total_price,
            issued_at=p.issued_at.isoformat(),
            notes=p.notes,
            details=details,
        )
    return RecordOut(
        record_id=r.record_id,
        patient_name=patient.real_name,
        gender=patient.gender,
        doctor_name=doctor.real_name,
        dept_name=dept.dept_name,
        visit_time=r.visit_time.isoformat(),
        chief_complaint=r.chief_complaint,
        diagnosis=r.diagnosis,
        treatment_plan=r.treatment_plan,
        notes=r.notes,
        prescription=presc_out,
    )


@router.post("", status_code=201)
def create_record(
    body: RecordCreate,
    current_user: Users = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if doctor is None:
        raise AppError(40401, "医生档案不存在", 404)
    appt = db.get(Appointment, body.appointment_id)
    if appt is None:
        raise AppError(40401, "预约不存在", 404)
    schedule = db.get(Schedule, appt.schedule_id)
    if schedule.doctor_id != doctor.doctor_id:
        raise AppError(40001, "该预约不属于您的排班", 403)
    if appt.medical_record:
        raise AppError(40901, "该预约已存在病历", 409)
    record = MedicalRecord(
        appointment_id=body.appointment_id,
        doctor_id=doctor.doctor_id,
        patient_id=appt.patient_id,
        chief_complaint=body.chief_complaint,
        diagnosis=body.diagnosis,
        treatment_plan=body.treatment_plan,
        notes=body.notes,
    )
    db.add(record)
    appt.status = "已就诊"
    db.commit()
    db.refresh(record)
    return Resp.created(
        data={
            "record_id": record.record_id,
            "appointment_id": record.appointment_id,
            "patient_name": db.get(Patient, record.patient_id).real_name,
            "visit_time": record.visit_time.isoformat(),
        },
        message="病历创建成功",
    )


@router.get("/{record_id}")
def get_record(
    record_id: int,
    current_user: Users = Depends(require_role("patient", "doctor", "admin")),
    db: Session = Depends(get_db),
):
    record = db.get(MedicalRecord, record_id)
    if record is None:
        raise AppError(40401, "病历不存在", 404)
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
        if patient is None or record.patient_id != patient.patient_id:
            raise AppError(40302, "无权查看他人病历", 403)
    elif current_user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
        if doctor is None or record.doctor_id != doctor.doctor_id:
            raise AppError(40302, "无权查看他人病历", 403)
    return Resp.ok(data=_build_record_out(record, db))


@router.put("/{record_id}")
def update_record(
    record_id: int,
    body: RecordUpdate,
    current_user: Users = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    record = db.get(MedicalRecord, record_id)
    if record is None:
        raise AppError(40401, "病历不存在", 404)
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if doctor is None or record.doctor_id != doctor.doctor_id:
        raise AppError(40302, "无权修改他人病历", 403)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(record, k, v)
    db.commit()
    return Resp.ok(data=None, message="病历更新成功")
