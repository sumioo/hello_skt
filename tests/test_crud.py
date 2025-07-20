import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import User, RoleEnum, StatusEnum
from app.crud import create_user, get_user, list_users, update_user_role, delete_user

# 使用 SQLite 内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine(event_loop):
    # 显式传递事件循环
    engine = create_async_engine(
        TEST_DATABASE_URL, 
        echo=True,
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # 确保在同一个事件循环中关闭会话
        await session.close()

# 添加一个显式的事件循环fixture
@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环，供所有测试使用"""
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_crud_operations(session: AsyncSession):
    print(session, '---------')
    # 创建
    user = await create_user(session, name="张三", status=StatusEnum.ACTIVE, role=RoleEnum.ADMIN)
    assert user.id is not None
    assert user.name == "张三"
    assert user.status == StatusEnum.ACTIVE
    assert user.role == RoleEnum.ADMIN

    # 读取
    fetched = await get_user(session, user.id)
    assert fetched is not None
    assert fetched.id == user.id

    # 列表
    users = await list_users(session)
    assert len(users) >= 1

    # 更新
    updated = await update_user_role(session, user.id, RoleEnum.USER.value)
    assert updated.role == RoleEnum.USER

    # 删除
    deleted = await delete_user(session, user.id)
    assert deleted
    assert await get_user(session, user.id) is None