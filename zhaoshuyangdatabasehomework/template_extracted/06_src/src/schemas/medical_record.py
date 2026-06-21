from __future__ import annotations
from typing import Optional, List, Any
from pydantic import BaseModel
from .prescription import PrescriptionOut


class RecordCreate(BaseModel):
    appointment_id: int
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None


class RecordUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None


class RecordOut(BaseModel):
    record_id: int
    patient_name: str
    gender: str
    doctor_name: str
    dept_name: str
    visit_time: str
    chief_complaint: Optional[str]
    diagnosis: Optional[str]
    treatment_plan: Optional[str]
    notes: Optional[str]
    prescription: Optional[PrescriptionOut]
