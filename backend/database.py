import aiosqlite
from datetime import datetime
from typing import List, Optional
from models import Task, Room

DATABASE_URL = "todo.db"

class Database:
    @staticmethod
    async def init_db():
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL,
                    active_users TEXT DEFAULT '[]'
                )
            """)
            await db.execute("""
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
            await db.commit()

    @staticmethod
    async def get_room(token: str) -> Optional[Room]:
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM rooms WHERE token = ?", (token,)
            )
            row = await cursor.fetchone()
            if row:
                return Room(
                    id=row['id'],
                    token=row['token'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    active_users=eval(row['active_users'])
                )
            return None

    @staticmethod
    async def create_room(token: str) -> Room:
        async with aiosqlite.connect(DATABASE_URL) as db:
            created_at = datetime.utcnow()
            cursor = await db.execute(
                "INSERT INTO rooms (token, created_at) VALUES (?, ?)",
                (token, created_at.isoformat())
            )
            await db.commit()
            return Room(
                id=cursor.lastrowid,
                token=token,
                created_at=created_at,
                active_users=[]
            )

    @staticmethod
    async def update_room_users(room_id: int, active_users: List[str]):
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute(
                "UPDATE rooms SET active_users = ? WHERE id = ?",
                (str(active_users), room_id)
            )
            await db.commit()

    @staticmethod
    async def get_tasks(room_id: str, include_deleted: bool = False) -> List[Task]:
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            if include_deleted:
                query = "SELECT * FROM tasks WHERE room_id = ? ORDER BY created_at DESC"
            else:
                query = "SELECT * FROM tasks WHERE room_id = ? AND is_deleted = 0 ORDER BY created_at DESC"
            cursor = await db.execute(query, (room_id,))
            rows = await cursor.fetchall()
            return [
                Task(
                    id=row['id'],
                    text=row['text'],
                    completed=bool(row['completed']),
                    creator=row['creator'],
                    room_id=row['room_id'],
                    priority=row['priority'] or 'medium',
                    due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
                    tags=eval(row['tags']) if row['tags'] else [],
                    description=row['description'],
                    is_deleted=bool(row['is_deleted']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    deleted_at=datetime.fromisoformat(row['deleted_at']) if row['deleted_at'] else None
                )
                for row in rows
            ]
    
    @staticmethod
    async def get_task_by_id(task_id: int) -> Optional[Task]:
        """根据ID获取单个任务"""
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = await cursor.fetchone()
            if row:
                return Task(
                    id=row['id'],
                    text=row['text'],
                    completed=bool(row['completed']),
                    creator=row['creator'],
                    room_id=row['room_id'],
                    priority=row['priority'] or 'medium',
                    due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
                    tags=eval(row['tags']) if row['tags'] else [],
                    description=row['description'],
                    is_deleted=bool(row['is_deleted']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    deleted_at=datetime.fromisoformat(row['deleted_at']) if row['deleted_at'] else None
                )
            return None

    @staticmethod
    async def create_task(text: str, creator: str, room_id: str, priority: str = 'medium', 
                         due_date: Optional[datetime] = None, tags: List[str] = None, 
                         description: Optional[str] = None) -> Task:
        async with aiosqlite.connect(DATABASE_URL) as db:
            created_at = datetime.utcnow()
            tags_str = str(tags or [])
            cursor = await db.execute(
                """INSERT INTO tasks (text, creator, room_id, priority, due_date, tags, description, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (text, creator, room_id, priority, 
                 due_date.isoformat() if due_date else None, 
                 tags_str, description, created_at.isoformat())
            )
            await db.commit()
            return Task(
                id=cursor.lastrowid,
                text=text,
                completed=False,
                creator=creator,
                room_id=room_id,
                priority=priority,
                due_date=due_date,
                tags=tags or [],
                description=description,
                is_deleted=False,
                created_at=created_at
            )

    @staticmethod
    async def update_task(task_id: int, **kwargs) -> Optional[Task]:
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            
            # 构建动态更新语句
            update_fields = []
            update_values = []
            
            for field, value in kwargs.items():
                if field == 'tags' and value is not None:
                    update_fields.append(f"{field} = ?")
                    update_values.append(str(value))
                elif field == 'due_date' and value is not None:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value.isoformat() if isinstance(value, datetime) else value)
                elif value is not None:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if update_fields:
                # 添加更新时间
                update_fields.append("updated_at = ?")
                update_values.append(datetime.utcnow().isoformat())
                
                update_values.append(task_id)
                query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
                await db.execute(query, update_values)
                await db.commit()
            
            cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = await cursor.fetchone()
            if row:
                return Task(
                    id=row['id'],
                    text=row['text'],
                    completed=bool(row['completed']),
                    creator=row['creator'],
                    room_id=row['room_id'],
                    priority=row['priority'] or 'medium',
                    due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
                    tags=eval(row['tags']) if row['tags'] else [],
                    description=row['description'],
                    is_deleted=bool(row['is_deleted']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    deleted_at=datetime.fromisoformat(row['deleted_at']) if row['deleted_at'] else None
                )
            return None

    @staticmethod
    async def delete_task(task_id: int, soft_delete: bool = True):
        async with aiosqlite.connect(DATABASE_URL) as db:
            if soft_delete:
                # 软删除：标记为已删除
                deleted_at = datetime.utcnow()
                await db.execute(
                    "UPDATE tasks SET is_deleted = 1, deleted_at = ? WHERE id = ?",
                    (deleted_at.isoformat(), task_id)
                )
            else:
                # 硬删除：永久删除
                await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            await db.commit()
    
    @staticmethod
    async def restore_task(task_id: int):
        """恢复已删除的任务"""
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute(
                "UPDATE tasks SET is_deleted = 0, deleted_at = NULL WHERE id = ?",
                (task_id,)
            )
            await db.commit()
    
    @staticmethod
    async def get_deleted_tasks(room_id: str) -> List[Task]:
        """获取垃圾桶中的任务"""
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE room_id = ? AND is_deleted = 1 ORDER BY deleted_at DESC",
                (room_id,)
            )
            rows = await cursor.fetchall()
            return [
                Task(
                    id=row['id'],
                    text=row['text'],
                    completed=bool(row['completed']),
                    creator=row['creator'],
                    room_id=row['room_id'],
                    priority=row['priority'] or 'medium',
                    due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
                    tags=eval(row['tags']) if row['tags'] else [],
                    description=row['description'],
                    is_deleted=bool(row['is_deleted']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    deleted_at=datetime.fromisoformat(row['deleted_at']) if row['deleted_at'] else None
                )
                for row in rows
            ]