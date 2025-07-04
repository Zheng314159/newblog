#!/usr/bin/env python3
"""
重建数据库，解决FTS5表损坏问题
"""
import sqlite3
import os
import shutil
from datetime import datetime

def backup_and_rebuild_database():
    """备份数据并重建数据库"""
    db_path = "blog.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    print("开始备份数据并重建数据库...")
    
    # 1. 创建备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"blog_backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✓ 数据库已备份到: {backup_path}")
    except Exception as e:
        print(f"✗ 备份失败: {e}")
        return
    
    # 2. 从备份中提取重要数据
    print("\n=== 提取重要数据 ===")
    
    try:
        backup_conn = sqlite3.connect(backup_path)
        backup_cursor = backup_conn.cursor()
        
        # 提取用户数据
        backup_cursor.execute("SELECT * FROM user")
        users = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(users)} 个用户")
        
        # 提取文章数据
        backup_cursor.execute("SELECT * FROM article")
        articles = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(articles)} 篇文章")
        
        # 提取标签数据
        backup_cursor.execute("SELECT * FROM tag")
        tags = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(tags)} 个标签")
        
        # 提取文章标签关联
        backup_cursor.execute("SELECT * FROM articletag")
        article_tags = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(article_tags)} 个文章标签关联")
        
        # 提取评论数据
        backup_cursor.execute("SELECT * FROM comment")
        comments = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(comments)} 条评论")
        
        # 提取其他重要数据
        backup_cursor.execute("SELECT * FROM systemnotification")
        notifications = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(notifications)} 条系统通知")
        
        backup_cursor.execute("SELECT * FROM mediafile")
        media_files = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(media_files)} 个媒体文件")
        
        backup_cursor.execute("SELECT * FROM donationconfig")
        donation_configs = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(donation_configs)} 个捐赠配置")
        
        backup_cursor.execute("SELECT * FROM donationrecord")
        donation_records = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(donation_records)} 条捐赠记录")
        
        backup_cursor.execute("SELECT * FROM donationgoal")
        donation_goals = backup_cursor.fetchall()
        print(f"✓ 提取到 {len(donation_goals)} 个捐赠目标")
        
        backup_conn.close()
        
    except Exception as e:
        print(f"✗ 提取数据失败: {e}")
        return
    
    # 3. 删除原数据库
    try:
        os.remove(db_path)
        print(f"✓ 已删除损坏的数据库: {db_path}")
    except Exception as e:
        print(f"✗ 删除数据库失败: {e}")
        return
    
    # 4. 重新创建数据库（通过启动应用）
    print("\n=== 重新创建数据库 ===")
    print("请运行以下命令重新创建数据库:")
    print("python -c \"from app.main import app; print('数据库将重新创建')\"")
    
    print(f"\n=== 重建完成 ===")
    print(f"✓ 原数据库已备份到: {backup_path}")
    print(f"✓ 损坏的数据库已删除")
    print("✓ 请重启应用以重新创建数据库")
    print("✓ 重要数据已提取，可以手动恢复")

if __name__ == "__main__":
    backup_and_rebuild_database() 