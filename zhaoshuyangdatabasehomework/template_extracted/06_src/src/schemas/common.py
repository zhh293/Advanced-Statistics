from __future__ import annotations
from typing import Any, Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class Resp(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "success", code: int = 200) -> "Resp":
        return cls(code=code, message=message, data=data)

    @classmethod
    def created(cls, data: Any = None, message: str = "创建成功") -> "Resp":
        return cls(code=201, message=message, data=data)

    @classmethod
    def fail(cls, code: int, message: str) -> "Resp":
        return cls(code=code, message=message, data=None)


class PagedData(BaseModel, Generic[T]):
    list: List[T]
    total: int
    page: int
    page_size: int
