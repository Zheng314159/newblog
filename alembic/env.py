from logging.config import fileConfig
from pathlib import Path
from alembic import context
from dotenv import load_dotenv
from sqlmodel import SQLModel
import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import create_async_engine  # ✅ 注意

# 添加项目根目录
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 动态加载 .env 或 .env.{ENVIRONMENT}
env = os.getenv("ENVIRONMENT", "development").lower()
env_file = Path(".") / f".env.{env}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(Path(".") / ".env")

# ✅ 导入你的 config
from app.core.config import settings
from app.models import __all_models__  # 自动引入所有 SQLModel 模型

# Alembic config
config = context.config
fileConfig(config.config_file_name, encoding=settings.python_io_encoding)

# 设置 sqlalchemy.url（即使是 asyncpg，也需要设为 sync URL 用于 Alembic 的兼容处理）
config.set_main_option("sqlalchemy.url", settings.database_url.replace("asyncpg", "psycopg2"))

target_metadata = SQLModel.metadata

def include_object(object, name, type_, reflected, compare_to):
    if name and name.startswith("articles_fts"):
        return False
    return True

def run_migrations_offline():
    """离线迁移：不连接数据库"""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """同步迁移逻辑"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """在线迁移"""
    engine = create_async_engine(settings.database_url, echo=False)  # ✅ 动态创建
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
