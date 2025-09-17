from logging.config import fileConfig
from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection
from sqlmodel import SQLModel
from alembic import context

# Alembic 配置
config = context.config
fileConfig(config.config_file_name)
import app.models  # 导入所有 model
from app.models import Base

target_metadata = Base.metadata

# 离线迁移
def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

# 在线迁移（使用同步 Engine 避免 greenlet_spawn 错误）
def run_migrations_online():
    # 使用同步 Engine 而非 AsyncEngine
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()