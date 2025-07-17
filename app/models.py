from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import TINYINT


# 数字类型枚举
class StatusEnum(int, Enum):
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
    status: StatusEnum = Field(
        default=StatusEnum.PENDING,
        sa_column=Column(TINYINT(unsigned=True), comment=enum_comment(StatusEnum), default=StatusEnum.PENDING.value),
    )
    role: RoleEnum = Field(
        default=RoleEnum.USER,
        sa_column=Column(String(50), comment=enum_comment(RoleEnum), default=RoleEnum.USER.value),
    )
