from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users, Medicine
from ..dependencies import require_role
from ..exceptions import AppError
from ..schemas.common import Resp, PagedData
from ..schemas.medicine import MedicineOut

router = APIRouter(prefix="/medicines", tags=["药品"])


@router.get("")
def list_medicines(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: Users = Depends(require_role("doctor", "admin")),
    db: Session = Depends(get_db),
):
    q = db.query(Medicine)
    if keyword:
        q = q.filter(Medicine.medicine_name.contains(keyword))
    if category:
        q = q.filter(Medicine.category == category)
    if in_stock is True:
        q = q.filter(Medicine.stock > 0)
    total = q.count()
    medicines = q.offset((page - 1) * page_size).limit(page_size).all()
    return Resp.ok(data=PagedData(
        list=[MedicineOut.model_validate(m) for m in medicines],
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.get("/{medicine_id}")
def get_medicine(
    medicine_id: int,
    current_user: Users = Depends(require_role("doctor", "admin")),
    db: Session = Depends(get_db),
):
    med = db.get(Medicine, medicine_id)
    if med is None:
        raise AppError(40401, "药品不存在", 404)
    return Resp.ok(data=MedicineOut.model_validate(med))
