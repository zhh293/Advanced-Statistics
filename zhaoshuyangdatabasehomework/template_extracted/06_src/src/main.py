from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .exceptions import AppError, app_error_handler
from .routers import (
    auth, patients, departments, doctors,
    schedules, appointments, medical_records,
    prescriptions, medicines, admin,
)

app = FastAPI(
    title="医院预约系统 API",
    version="1.0.0",
    description="基于 FastAPI + PostgreSQL 的医院预约系统后端",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

PREFIX = "/api/v1"
app.include_router(auth.router,            prefix=PREFIX)
app.include_router(patients.router,        prefix=PREFIX)
app.include_router(departments.router,     prefix=PREFIX)
app.include_router(doctors.router,         prefix=PREFIX)
app.include_router(schedules.router,       prefix=PREFIX)
app.include_router(appointments.router,    prefix=PREFIX)
app.include_router(medical_records.router, prefix=PREFIX)
app.include_router(prescriptions.router,   prefix=PREFIX)
app.include_router(medicines.router,       prefix=PREFIX)
app.include_router(admin.router,           prefix=PREFIX)


@app.get("/")
def health():
    return {"status": "ok", "message": "医院预约系统后端运行中"}
