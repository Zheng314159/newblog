# scripts/init_db.py

import os
import sys
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import psycopg2

# 加载 .env 或 .env.{ENVIRONMENT}
env = os.getenv("ENVIRONMENT", "development").lower()
env_file = Path(".") / f".env.{env}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv(Path(".") / ".env")

# 获取数据库地址
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL 未设置")
    sys.exit(1)

# 如果是 SQLite，跳过数据库创建
if database_url.startswith("sqlite"):
    print("📝 当前使用 SQLite，无需初始化数据库")
else:
    # 解析 PostgreSQL URL
    parsed = urlparse(database_url.replace("+asyncpg", ""))
    db_name = parsed.path.lstrip("/")
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432

    def wait_for_postgres(timeout=30):
        """等待 PostgreSQL 启动"""
        print("⏳ 等待 PostgreSQL 启动...")
        for i in range(timeout):
            try:
                conn = psycopg2.connect(
                    dbname="postgres",
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                conn.close()
                print("✅ PostgreSQL 已就绪")
                return
            except Exception:
                time.sleep(1)
        print("❌ PostgreSQL 启动超时")
        sys.exit(1)

    def create_database_if_not_exists():
        """如果数据库不存在则创建"""
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.autocommit = True
            cur = conn.cursor()
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

    wait_for_postgres()
    create_database_if_not_exists()


def upgrade_alembic():
    """运行 Alembic 升级命令"""
    print("🚀 正在运行 Alembic 数据库迁移...")
    env_copy = os.environ.copy()
    env_copy["ENVIRONMENT"] = env
    try:
        subprocess.run(["alembic", "upgrade", "head"], env=env_copy, check=True)
        print("✅ Alembic 迁移成功")
    except subprocess.CalledProcessError as e:
        print("❌ Alembic 执行失败：", e)
        sys.exit(1)


if __name__ == "__main__":
    upgrade_alembic()
    print("🎉 数据库初始化完成")
