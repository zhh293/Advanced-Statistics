from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Department, Doctor, Room
from ..exceptions import AppError
from ..schemas.common import Resp
from ..schemas.department import DeptOut, DeptDetail, RoomItem, DoctorBrief

router = APIRouter(prefix="/departments", tags=["科室"])


@router.get("")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    result = []
    for d in depts:
        count = (
            db.query(Doctor)
            .filter(Doctor.dept_id == d.dept_id, Doctor.is_active == True)
            .count()
        )
        result.append(DeptOut(
            dept_id=d.dept_id,
            dept_name=d.dept_name,
            description=d.description,
            floor_no=d.floor_no,
            doctor_count=count,
        ))
    return Resp.ok(data=result)


@router.get("/{dept_id}")
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.get(Department, dept_id)
    if dept is None:
        raise AppError(40401, "科室不存在", 404)
    rooms = [RoomItem.model_validate(r) for r in dept.rooms]
    doctors = [
        DoctorBrief(
            doctor_id=d.doctor_id,
            real_name=d.real_name,
            title=d.title,
            specialty=d.specialty,
        )
        for d in dept.doctors
        if d.is_active
    ]
    return Resp.ok(data=DeptDetail(
        dept_id=dept.dept_id,
        dept_name=dept.dept_name,
        description=dept.description,
        floor_no=dept.floor_no,
        rooms=rooms,
        doctors=doctors,
    ))
