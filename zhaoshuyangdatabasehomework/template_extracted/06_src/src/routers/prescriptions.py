from __future__ import annotations
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (
    Users, Patient, Doctor, MedicalRecord,
    Prescription, PrescriptionDetail, Medicine,
)
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp
from ..schemas.prescription import PrescriptionCreate, PrescriptionOut, DetailOut

router = APIRouter(prefix="/prescriptions", tags=["处方"])


@router.post("", status_code=201)
def create_prescription(
    body: PrescriptionCreate,
    current_user: Users = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if doctor is None:
        raise AppError(40401, "医生档案不存在", 404)
    record = db.get(MedicalRecord, body.record_id)
    if record is None:
        raise AppError(40401, "病历不存在", 404)
    if record.doctor_id != doctor.doctor_id:
        raise AppError(40301, "无权为他人病历开具处方", 403)
    if record.prescription:
        raise AppError(40901, "该病历已存在处方", 409)

    total = Decimal("0")
    detail_data: list[tuple[Medicine, object, Decimal]] = []
    for item in body.details:
        med = db.get(Medicine, item.medicine_id)
        if med is None:
            raise AppError(40401, f"药品ID {item.medicine_id} 不存在", 404)
        if med.stock < item.quantity:
            raise AppError(42201, f"药品库存不足：{med.medicine_name}", 422)
        subtotal = med.price * item.quantity
        total += subtotal
        detail_data.append((med, item, subtotal))

    presc = Prescription(
        record_id=body.record_id,
        doctor_id=doctor.doctor_id,
        total_price=total,
        notes=body.notes,
    )
    db.add(presc)
    db.flush()  # 获取 prescription_id

    for med, item, subtotal in detail_data:
        d = PrescriptionDetail(
            prescription_id=presc.prescription_id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            dosage=item.dosage,
            days=item.days,
            subtotal=subtotal,
        )
        db.add(d)
        med.stock -= item.quantity

    db.commit()
    db.refresh(presc)

    real_details = [
        DetailOut(
            detail_id=d.detail_id,
            medicine_name=d.medicine.medicine_name,
            specification=d.medicine.specification,
            quantity=d.quantity,
            dosage=d.dosage,
            days=d.days,
            subtotal=d.subtotal,
        )
        for d in presc.details
    ]
    return Resp.created(
        data=PrescriptionOut(
            prescription_id=presc.prescription_id,
            record_id=presc.record_id,
            total_price=presc.total_price,
            issued_at=presc.issued_at.isoformat(),
            notes=presc.notes,
            details=real_details,
        ),
        message="处方开具成功",
    )


@router.get("/{prescription_id}")
def get_prescription(
    prescription_id: int,
    current_user: Users = Depends(require_role("patient", "doctor", "admin")),
    db: Session = Depends(get_db),
):
    presc = db.get(Prescription, prescription_id)
    if presc is None:
        raise AppError(40401, "处方不存在", 404)
    if current_user.role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
        record = db.get(MedicalRecord, presc.record_id)
        if patient is None or record.patient_id != patient.patient_id:
            raise AppError(40302, "无权查看他人处方", 403)
    elif current_user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
        if doctor is None or presc.doctor_id != doctor.doctor_id:
            raise AppError(40302, "无权查看他人处方", 403)
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
        for d in presc.details
    ]
    return Resp.ok(data=PrescriptionOut(
        prescription_id=presc.prescription_id,
        record_id=presc.record_id,
        total_price=presc.total_price,
        issued_at=presc.issued_at.isoformat(),
        notes=presc.notes,
        details=details,
    ))
