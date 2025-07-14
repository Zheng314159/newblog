from logging.config import fileConfig
from pathlib import Path
from alembic import context
from dotenv import load_dotenv
from sqlmodel import SQLModel
import asyncio
import os
import sys

# 添加你的项目根目录到 sys.path，确保导入正常
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 自动加载 .env 或 .env.{environment}
env = os.getenv("ENVIRONMENT", "development").lower()
env_file = Path(".") / f".env.{env}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(Path(".") / ".env")
# 加载自定义配置和模型
from app.core.config import settings  # 用于获取 DATABASE_URL
from app.core.database import engine  # 如果你已有 async engine，可以用这个
from app.models import __all_models__  # 确保 models/__init__.py 引入了所有模型

# Alembic 配置对象
config = context.config

# 加载 logging 配置
fileConfig(config.config_file_name)

# 设置 sqlalchemy.url（用于兼容 offline 模式）
config.set_main_option("sqlalchemy.url", settings.database_url)

# 指定目标 metadata（用于自动生成迁移）
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """离线模式：生成 SQL 文件，而不连接数据库"""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """同步运行迁移（由 async wrapper 调用）"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """在线模式：连接数据库执行迁移"""
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
