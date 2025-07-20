from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, StatusEnum, RoleEnum

async def create_user(session: AsyncSession, name: str,
                      status: StatusEnum = StatusEnum.PENDING,
                      role: RoleEnum = RoleEnum.USER) -> User:
    user = User(name=name, status=status.value, role=role.value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.exec(select(User).where(User.id == user_id))
    return result.first()

async def list_users(session: AsyncSession) -> List[User]:
    result = await session.exec(select(User))
    return result.all()

async def update_user_role(session: AsyncSession, user_id: int, new_role: RoleEnum) -> Optional[User]:
    user = await get_user(session, user_id)
    if not user:
        return None
    user.role = new_role
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def delete_user(session: AsyncSession, user_id: int) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True