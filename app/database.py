from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.engine import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+asyncmy://root:qwer4321@localhost:3306/mydb"

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

async_session: sessionmaker[_AsyncSession] = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # 如果插入初始数据，可在此处
        await conn.run_sync(SQLModel.metadata.create_all)

# 在依赖中使用：
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session