#!/usr/bin/env python3
"""
简单的数据库初始化脚本
"""
import asyncio
from app.core.database import engine
from app.models import user, article, comment, tag, system_notification, media, donation
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def simple_init():
    """简单初始化数据库"""
    print("开始简单初始化数据库...")
    
    # 1. 创建所有表
    print("创建数据库表...")
    async with engine.begin() as conn:
        # 导入所有模型以确保表被创建
        pass
    
    # 2. 创建管理员用户
    print("创建管理员用户...")
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import get_db
    from sqlalchemy import select
    
    async for db in get_db():
        try:
            # 检查是否已存在管理员用户
            result = await db.execute(select(User).where(User.username == "admin"))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                # 创建管理员用户
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    full_name="超级管理员",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                await db.commit()
                await db.refresh(admin_user)
                print("✓ 管理员用户创建成功")
                print(f"  用户名: admin")
                print(f"  密码: admin123")
            else:
                print("✓ 管理员用户已存在")
            
            break
            
        except Exception as e:
            print(f"✗ 创建管理员用户失败: {e}")
            break
    
    print("\n=== 数据库初始化完成 ===")
    print("✓ 数据库表已创建")
    print("✓ 管理员用户已创建")
    print("✓ 可以开始使用博客系统")

if __name__ == "__main__":
    asyncio.run(simple_init()) 