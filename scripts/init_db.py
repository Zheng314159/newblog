# scripts/init_db.py

import os
import sys
import asyncio
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import subprocess
from urllib.parse import urlparse

# 加载环境变量
env = os.getenv("ENVIRONMENT", "development").lower()
env_file = Path(".") / f".env.{env}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(Path(".") / ".env")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL 未设置")
    sys.exit(1)

# 解析数据库连接参数
parsed = urlparse(database_url.replace("+asyncpg", ""))
db_name = parsed.path.lstrip("/")
user = parsed.username
password = parsed.password
host = parsed.hostname or "localhost"
port = parsed.port or 5432

def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    try:
        # 连接 postgres 默认数据库
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cur = conn.cursor()
        # 检查数据库是否存在
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        exists = cur.fetchone()
        if not exists:
            print(f"🛠️  正在创建数据库 {db_name}...")
            cur.execute(f"CREATE DATABASE {db_name};")
        else:
            print(f"✅ 数据库 {db_name} 已存在")
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ 数据库连接或创建失败：", e)
        sys.exit(1)

def upgrade_alembic():
    """运行 Alembic 升级命令"""
    print("🚀 正在运行 Alembic 数据库迁移...")
    env_copy = os.environ.copy()
    env_copy["ENVIRONMENT"] = env
    subprocess.run(["alembic", "upgrade", "head"], env=env_copy, check=True)

if __name__ == "__main__":
    if "postgresql" in database_url:
        create_database_if_not_exists()
    upgrade_alembic()
    print("🎉 数据库初始化完成")
