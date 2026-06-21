from __future__ import annotations
from typing import Callable
from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy.orm import Session
from .database import get_db
from .models import Users
from .auth import decode_token
from .exceptions import AppError


def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> Users:
    if not authorization.startswith("Bearer "):
        raise AppError(40103, "未提供认证信息", 401)
    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_token(token)
        user_id: int = int(payload["sub"])
    except (JWTError, KeyError):
        raise AppError(40102, "Token已过期，请重新登录", 401)
    user = db.get(Users, user_id)
    if user is None:
        raise AppError(40401, "用户不存在", 404)
    return user


def require_role(*roles: str) -> Callable:
    def checker(current_user: Users = Depends(get_current_user)) -> Users:
        if current_user.role not in roles:
            raise AppError(40301, "权限不足", 403)
        return current_user
    return checker
