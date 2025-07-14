from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskBase(BaseModel):
    text: str
    completed: bool = False
    creator: str
    room_id: str
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = []
    description: Optional[str] = None
    is_deleted: bool = False

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None

class RoomBase(BaseModel):
    token: str

class Room(RoomBase):
    id: int
    created_at: datetime
    active_users: List[str] = []

    class Config:
        orm_mode = True

class RoomCreate(RoomBase):
    pass