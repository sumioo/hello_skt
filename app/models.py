from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, SmallInteger, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

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


class User(Base):
    __tablename__ = "user"

    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    # id: Optional[str] = Column(String(length=20), nullable=False, primary_key=True)
    name: str = Column(String(length=20), nullable=False)
    status: StatusEnum = Column(SmallInteger, default=StatusEnum.PENDING, comment=f"用户状态 {enum_comment(StatusEnum)}")
    role: RoleEnum = Column(String(20), default=RoleEnum.USER, comment=f"用户角色 {enum_comment(RoleEnum)}")
