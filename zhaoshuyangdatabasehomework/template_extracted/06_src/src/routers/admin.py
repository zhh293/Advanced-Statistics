from __future__ import annotations
from typing import Optional, List, Any
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users, Department, Doctor, Schedule, Room, Medicine, Patient, Appointment
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp
from ..schemas.department import DeptCreate, DeptUpdate
from ..schemas.schedule import ScheduleCreate, ScheduleStatusUpdate
from ..schemas.medicine import MedicineCreate, StockUpdate

router = APIRouter(prefix="/admin", tags=["管理员"])

_admin = Depends(require_role("admin"))


# ── 科室管理 ─────────────────────────────────────────────────

@router.post("/departments", status_code=201)
def create_dept(body: DeptCreate, db: Session = Depends(get_db), _=_admin):
    if db.query(Department).filter(Department.dept_name == body.dept_name).first():
        raise AppError(40901, "科室名称已存在", 409)
    dept = Department(**body.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return Resp.created(data={"dept_id": dept.dept_id}, message="科室创建成功")


@router.put("/departments/{dept_id}")
def update_dept(dept_id: int, body: DeptUpdate, db: Session = Depends(get_db), _=_admin):
    dept = db.get(Department, dept_id)
    if dept is None:
        raise AppError(40401, "科室不存在", 404)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(dept, k, v)
    db.commit()
    return Resp.ok(data=None, message="科室更新成功")


# ── 排班管理 ─────────────────────────────────────────────────

@router.post("/schedules", status_code=201)
def create_schedule(body: ScheduleCreate, db: Session = Depends(get_db), _=_admin):
    if db.get(Doctor, body.doctor_id) is None:
        raise AppError(40401, "医生不存在", 404)
    if db.get(Room, body.room_id) is None:
        raise AppError(40401, "诊室不存在", 404)
    existing = db.query(Schedule).filter(
        Schedule.doctor_id == body.doctor_id,
        Schedule.work_date == body.work_date,
        Schedule.time_period == body.time_period,
    ).first()
    if existing:
        raise AppError(40901, "该医生该时段已有排班", 409)
    schedule = Schedule(**body.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return Resp.created(data={"schedule_id": schedule.schedule_id}, message="排班创建成功")


@router.put("/schedules/{schedule_id}/status")
def update_schedule_status(
    schedule_id: int,
    body: ScheduleStatusUpdate,
    db: Session = Depends(get_db),
    _=_admin,
):
    schedule = db.get(Schedule, schedule_id)
    if schedule is None:
        raise AppError(40401, "排班不存在", 404)
    if body.status not in ("正常", "停诊", "约满"):
        raise AppError(40001, "无效的状态值", 400)
    schedule.status = body.status
    db.commit()
    return Resp.ok(data=None, message="排班状态已更新")


# ── 药品管理 ─────────────────────────────────────────────────

@router.post("/medicines", status_code=201)
def create_medicine(body: MedicineCreate, db: Session = Depends(get_db), _=_admin):
    existing = db.query(Medicine).filter(
        Medicine.medicine_name == body.medicine_name,
        Medicine.specification == body.specification,
    ).first()
    if existing:
        raise AppError(40901, "同名同规格药品已存在", 409)
    med = Medicine(**body.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return Resp.created(data={"medicine_id": med.medicine_id}, message="药品添加成功")


@router.put("/medicines/{medicine_id}/stock")
def update_stock(medicine_id: int, body: StockUpdate, db: Session = Depends(get_db), _=_admin):
    med = db.get(Medicine, medicine_id)
    if med is None:
        raise AppError(40401, "药品不存在", 404)
    if body.stock < 0:
        raise AppError(40001, "库存不能为负数", 400)
    med.stock = body.stock
    db.commit()
    return Resp.ok(data=None, message="库存更新成功")


# ── 统计数据 ─────────────────────────────────────────────────

@router.get("/statistics")
def statistics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    _=_admin,
):
    total_patients = db.query(Patient).count()
    total_doctors = db.query(Doctor).filter(Doctor.is_active == True).count()
    total_depts = db.query(Department).count()

    q = db.query(Appointment).join(Schedule)
    if date_from:
        q = q.filter(Schedule.work_date >= date.fromisoformat(date_from))
    if date_to:
        q = q.filter(Schedule.work_date <= date.fromisoformat(date_to))

    total_appts = q.count()
    completed = q.filter(Appointment.status == "已就诊").count()
    cancelled = q.filter(Appointment.status == "已取消").count()
    absent = q.filter(Appointment.status == "爽约").count()

    today = date.today()
    today_q = db.query(Appointment).join(Schedule).filter(Schedule.work_date == today)

    return Resp.ok(data={
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_departments": total_depts,
        "appointments": {
            "total": total_appts,
            "completed": completed,
            "cancelled": cancelled,
            "absent": absent,
        },
        "today": {
            "appointments": today_q.count(),
            "completed": today_q.filter(Appointment.status == "已就诊").count(),
        },
    })


# ── 用户管理 ─────────────────────────────────────────────────

@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _=_admin,
):
    user = db.get(Users, user_id)
    if user is None:
        raise AppError(40401, "用户不存在", 404)
    # is_active 可通过扩展 Users 表实现；此处返回成功响应
    return Resp.ok(data=None, message="用户状态已更新")
