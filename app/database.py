from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+asyncmy://root:qwer4321@localhost:3306/mydb"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
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