from __future__ import annotations
from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel


class MedicineCreate(BaseModel):
    medicine_name: str
    specification: str = ""
    unit: str
    price: Decimal
    stock: int = 0
    category: Optional[str] = None


class StockUpdate(BaseModel):
    stock: int


class MedicineOut(BaseModel):
    medicine_id: int
    medicine_name: str
    specification: str
    unit: str
    price: Decimal
    stock: int
    category: Optional[str]

    model_config = {"from_attributes": True}
