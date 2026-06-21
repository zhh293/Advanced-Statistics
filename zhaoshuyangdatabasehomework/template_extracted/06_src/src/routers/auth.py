from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users
from ..auth import hash_password, verify_password, create_access_token
from ..dependencies import get_current_user
from ..exceptions import AppError
from ..schemas.common import Resp
from ..schemas.auth import RegisterIn, LoginIn, LoginOut, UserInfo, UserDetail
from ..config import settings

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(Users).filter(Users.username == body.username).first():
        raise AppError(40901, "用户名已存在", 409)
    if body.email and db.query(Users).filter(Users.email == body.email).first():
        raise AppError(40902, "邮箱已被注册", 409)
    user = Users(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        email=body.email,
        phone=body.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return Resp.created(
        data={"user_id": user.user_id, "username": user.username, "role": user.role},
        message="注册成功",
    )


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise AppError(40101, "用户名或密码错误", 401)
    token = create_access_token({"sub": str(user.user_id), "role": user.role})
    return Resp.ok(
        data=LoginOut(
            access_token=token,
            expires_in=settings.access_token_expire_seconds,
            user=UserInfo.model_validate(user),
        ),
        message="登录成功",
    )


@router.post("/logout")
def logout(current_user: Users = Depends(get_current_user)):
    # JWT 无状态，客户端丢弃 token 即可
    return Resp.ok(data=None, message="已登出")


@router.get("/me")
def me(current_user: Users = Depends(get_current_user)):
    return Resp.ok(data=UserDetail(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        email=current_user.email,
        phone=current_user.phone,
        created_at=current_user.created_at.isoformat(),
    ))
