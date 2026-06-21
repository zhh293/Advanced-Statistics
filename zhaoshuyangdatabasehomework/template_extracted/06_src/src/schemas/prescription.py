from __future__ import annotations
from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel


class DetailIn(BaseModel):
    medicine_id: int
    quantity: int
    dosage: Optional[str] = None
    days: Optional[int] = None


class PrescriptionCreate(BaseModel):
    record_id: int
    notes: Optional[str] = None
    details: List[DetailIn]


class DetailOut(BaseModel):
    detail_id: int
    medicine_name: str
    specification: str
    quantity: int
    dosage: Optional[str]
    days: Optional[int]
    subtotal: Optional[Decimal]


class PrescriptionOut(BaseModel):
    prescription_id: int
    record_id: int
    total_price: Optional[Decimal]
    issued_at: str
    notes: Optional[str]
    details: List[DetailOut]
