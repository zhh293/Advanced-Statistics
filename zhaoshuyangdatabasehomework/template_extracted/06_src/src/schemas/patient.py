from __future__ import annotations
from typing import Optional, List, Any
from datetime import date
from pydantic import BaseModel


class PatientCreate(BaseModel):
    real_name: str
    id_card: str
    gender: str
    birth_date: Optional[date] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class PatientUpdate(BaseModel):
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class PatientOut(BaseModel):
    patient_id: int
    user_id: int
    real_name: str
    id_card: str
    gender: str
    birth_date: Optional[date]
    address: Optional[str]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]

    model_config = {"from_attributes": True}


class RecordSummary(BaseModel):
    record_id: int
    visit_time: str
    doctor_name: str
    dept_name: str
    diagnosis: Optional[str]
    has_prescription: bool
