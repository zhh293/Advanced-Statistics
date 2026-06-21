from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users, Patient, MedicalRecord, Doctor, Department
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp, PagedData
from ..schemas.patient import PatientCreate, PatientUpdate, PatientOut, RecordSummary

router = APIRouter(prefix="/patients", tags=["患者"])


def _get_patient(current_user: Users, db: Session) -> Patient:
    p = db.query(Patient).filter(Patient.user_id == current_user.user_id).first()
    if p is None:
        raise AppError(40001, "患者档案不存在，请先完善个人信息", 400)
    return p


@router.post("/profile", status_code=201)
def create_profile(
    body: PatientCreate,
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    if db.query(Patient).filter(Patient.user_id == current_user.user_id).first():
        raise AppError(40901, "档案已存在", 409)
    if db.query(Patient).filter(Patient.id_card == body.id_card).first():
        raise AppError(40902, "身份证号已被注册", 409)
    patient = Patient(user_id=current_user.user_id, **body.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return Resp.created(data=PatientOut.model_validate(patient), message="档案创建成功")


@router.get("/profile")
def get_profile(
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = _get_patient(current_user, db)
    return Resp.ok(data=PatientOut.model_validate(patient))


@router.put("/profile")
def update_profile(
    body: PatientUpdate,
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = _get_patient(current_user, db)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(patient, k, v)
    db.commit()
    return Resp.ok(data=None, message="档案更新成功")


@router.get("/records")
def get_records(
    page: int = 1,
    page_size: int = 20,
    current_user: Users = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = _get_patient(current_user, db)
    q = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient.patient_id)
        .order_by(MedicalRecord.visit_time.desc())
    )
    total = q.count()
    records = q.offset((page - 1) * page_size).limit(page_size).all()

    def _to_summary(r: MedicalRecord) -> RecordSummary:
        doctor = db.get(Doctor, r.doctor_id)
        dept = db.get(Department, doctor.dept_id)
        return RecordSummary(
            record_id=r.record_id,
            visit_time=r.visit_time.isoformat(),
            doctor_name=doctor.real_name,
            dept_name=dept.dept_name,
            diagnosis=r.diagnosis,
            has_prescription=r.prescription is not None,
        )

    return Resp.ok(data=PagedData(
        list=[_to_summary(r) for r in records],
        total=total,
        page=page,
        page_size=page_size,
    ))
