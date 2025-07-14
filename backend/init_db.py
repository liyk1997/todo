#!/usr/bin/env python3
"""
数据库初始化脚本
用于Docker容器启动时初始化数据库
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """初始化SQLite数据库"""
    db_path = Path(__file__).parent / "todo.db"
    
    # 如果数据库已存在，不需要重复初始化
    if db_path.exists():
        print(f"数据库已存在: {db_path}")
        return
    
    print(f"正在初始化数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 创建rooms表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL,
                active_users TEXT DEFAULT '[]'
            )
        """)
        
        # 创建tasks表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                creator TEXT NOT NULL,
                room_id TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                due_date TIMESTAMP,
                tags TEXT DEFAULT '[]',
                description TEXT,
                is_deleted BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                deleted_at TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("数据库初始化完成")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_database()