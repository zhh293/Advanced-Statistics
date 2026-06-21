from __future__ import annotations
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Integer, String, Boolean, Date, DateTime, Numeric, Text,
    ForeignKey, UniqueConstraint, CheckConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uk_user_username"),
        UniqueConstraint("email", name="uk_user_email"),
        CheckConstraint("role IN ('admin','patient','doctor')", name="chk_user_role"),
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="patient")
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    patient: Mapped["Optional[Patient]"] = relationship("Patient", back_populates="user", uselist=False)
    doctor: Mapped["Optional[Doctor]"] = relationship("Doctor", back_populates="user", uselist=False)


class Patient(Base):
    __tablename__ = "patient"
    __table_args__ = (
        UniqueConstraint("id_card", name="uk_patient_id_card"),
        UniqueConstraint("user_id", name="uk_patient_user"),
        CheckConstraint("gender IN ('男','女')", name="chk_patient_gender"),
    )

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    id_card: Mapped[str] = mapped_column(String(18), nullable=False)
    gender: Mapped[str] = mapped_column(String(4), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient")
    medical_records: Mapped[list["MedicalRecord"]] = relationship("MedicalRecord", back_populates="patient")


class Department(Base):
    __tablename__ = "department"
    __table_args__ = (UniqueConstraint("dept_name", name="uk_dept_name"),)

    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    floor_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    doctors: Mapped[list["Doctor"]] = relationship("Doctor", back_populates="department")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="department")


class Doctor(Base):
    __tablename__ = "doctor"
    __table_args__ = (
        UniqueConstraint("user_id", name="uk_doctor_user"),
        CheckConstraint(
            "title IN ('主任医师','副主任医师','主治医师','住院医师')",
            name="chk_doctor_title",
        ),
    )

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("department.dept_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    intro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["Users"] = relationship("Users", back_populates="doctor")
    department: Mapped["Department"] = relationship("Department", back_populates="doctors")
    schedules: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="doctor")
    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        "MedicalRecord", back_populates="doctor"
    )
    prescriptions: Mapped[list["Prescription"]] = relationship(
        "Prescription", back_populates="doctor"
    )


class Room(Base):
    __tablename__ = "room"
    __table_args__ = (UniqueConstraint("room_no", name="uk_room_no"),)

    room_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("department.dept_id"), nullable=False)
    room_name: Mapped[str] = mapped_column(String(50), nullable=False)
    room_no: Mapped[str] = mapped_column(String(20), nullable=False)
    floor_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    department: Mapped["Department"] = relationship("Department", back_populates="rooms")
    schedules: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="room")


class Schedule(Base):
    __tablename__ = "schedule"
    __table_args__ = (
        UniqueConstraint("doctor_id", "work_date", "time_period", name="uk_schedule"),
        CheckConstraint("time_period IN ('上午','下午','晚上')", name="chk_schedule_period"),
        CheckConstraint("max_patients > 0", name="chk_max_patients"),
        CheckConstraint("registered_count >= 0", name="chk_registered_gte_zero"),
        CheckConstraint("registered_count <= max_patients", name="chk_registered_le_max"),
        CheckConstraint("status IN ('正常','停诊','约满')", name="chk_schedule_status"),
    )

    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctor.doctor_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("room.room_id"), nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    time_period: Mapped[str] = mapped_column(String(10), nullable=False)
    max_patients: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    registered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="正常")

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
    room: Mapped["Room"] = relationship("Room", back_populates="schedules")
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="schedule"
    )


class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = (
        UniqueConstraint("schedule_id", "queue_no", name="uk_appt_queue"),
        UniqueConstraint("patient_id", "schedule_id", name="uk_appt_patient_schedule"),
        CheckConstraint("queue_no > 0", name="chk_queue_no"),
        CheckConstraint(
            "status IN ('待就诊','已就诊','已取消','爽约')", name="chk_appt_status"
        ),
    )

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patient.patient_id"), nullable=False
    )
    schedule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("schedule.schedule_id"), nullable=False
    )
    queue_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="待就诊")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="appointments")
    medical_record: Mapped["Optional[MedicalRecord]"] = relationship(
        "MedicalRecord", back_populates="appointment", uselist=False
    )


class MedicalRecord(Base):
    __tablename__ = "medicalrecord"
    __table_args__ = (UniqueConstraint("appointment_id", name="uk_record_appointment"),)

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("appointment.appointment_id"), nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctor.doctor_id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patient.patient_id"), nullable=False
    )
    visit_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    treatment_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    appointment: Mapped["Appointment"] = relationship(
        "Appointment", back_populates="medical_record"
    )
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="medical_records")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="medical_records")
    prescription: Mapped["Optional[Prescription]"] = relationship(
        "Prescription", back_populates="medical_record", uselist=False
    )


class Prescription(Base):
    __tablename__ = "prescription"
    __table_args__ = (
        UniqueConstraint("record_id", name="uk_prescription_record"),
        CheckConstraint("total_price >= 0", name="chk_total_price"),
    )

    prescription_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicalrecord.record_id"), nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctor.doctor_id"), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    total_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    medical_record: Mapped["MedicalRecord"] = relationship(
        "MedicalRecord", back_populates="prescription"
    )
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="prescriptions")
    details: Mapped[list["PrescriptionDetail"]] = relationship(
        "PrescriptionDetail", back_populates="prescription", cascade="all, delete-orphan"
    )


class Medicine(Base):
    __tablename__ = "medicine"
    __table_args__ = (
        UniqueConstraint("medicine_name", "specification", name="uk_medicine_name_spec"),
        CheckConstraint("price >= 0", name="chk_medicine_price"),
        CheckConstraint("stock >= 0", name="chk_medicine_stock"),
    )

    medicine_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specification: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    details: Mapped[list["PrescriptionDetail"]] = relationship(
        "PrescriptionDetail", back_populates="medicine"
    )


class PrescriptionDetail(Base):
    __tablename__ = "prescriptiondetail"
    __table_args__ = (
        UniqueConstraint(
            "prescription_id", "medicine_id", name="uk_detail_prescription_medicine"
        ),
        CheckConstraint("quantity > 0", name="chk_detail_quantity"),
        CheckConstraint("days > 0", name="chk_detail_days"),
        CheckConstraint("subtotal >= 0", name="chk_detail_subtotal"),
    )

    detail_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prescription.prescription_id", ondelete="CASCADE"),
        nullable=False,
    )
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicine.medicine_id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    dosage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    prescription: Mapped["Prescription"] = relationship(
        "Prescription", back_populates="details"
    )
    medicine: Mapped["Medicine"] = relationship("Medicine", back_populates="details")
