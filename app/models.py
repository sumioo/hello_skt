from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, SmallInteger


# 数字类型枚举
class StatusEnum(int, Enum):
    PENDING = 0
    ACTIVE = 1
    INACTIVE = 2


class StatusEnum2(int, Enum):
    PENDING = 0
    ACTIVE = 1
    INACTIVE = 2


# 字符串类型枚举
class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    GUEST = "guest"


def enum_comment(enum: type[Enum]) -> str:
    return " ".join([f"{item.value}: {item.name}" for item in enum])


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    status: StatusEnum = Field(default=StatusEnum.PENDING, description=f"用户状态 {enum_comment(StatusEnum)}", sa_column=Column(SmallInteger, comment=enum_comment(StatusEnum)))
    role: RoleEnum = Field(default=RoleEnum.USER, description=f"用户角色 {enum_comment(RoleEnum)}", sa_column=Column(String(20), comment=enum_comment(RoleEnum)))
