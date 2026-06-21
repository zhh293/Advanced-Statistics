from __future__ import annotations
from typing import Optional, List, Any
import re
from pydantic import BaseModel, field_validator


class RegisterIn(BaseModel):
    username: str
    password: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]{3,50}$", v):
            raise ValueError("用户名3-50位，仅含字母/数字/下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 32:
            raise ValueError("密码8-32位")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("patient", "doctor"):
            raise ValueError("role 只能是 patient 或 doctor")
        return v


class LoginIn(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    user_id: int
    username: str
    role: str

    model_config = {"from_attributes": True}


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserInfo


class UserDetail(BaseModel):
    user_id: int
    username: str
    role: str
    email: Optional[str]
    phone: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}
