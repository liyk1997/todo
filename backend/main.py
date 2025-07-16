import uvicorn
import secrets
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import TaskCreate, TaskUpdate, Task, Room, Priority
from database import Database
from websocket_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await Database.init_db()

# 房间管理接口
@app.post("/rooms/create", response_model=Room)
async def create_room():
    token = secrets.token_urlsafe(6)
    room = await Database.create_room(token)
    return room

@app.get("/rooms/{token}", response_model=Room)
async def get_room(token: str):
    room = await Database.get_room(token)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

# 任务管理接口
@app.get("/rooms/{room_id}/tasks", response_model=List[Task])
async def get_tasks(room_id: str):
    return await Database.get_tasks(room_id)

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    try:
        print(f"Received task data: {task.dict()}")
        new_task = await Database.create_task(
            text=task.text,
            creator=task.creator,
            room_id=task.room_id,
            priority=task.priority,
            due_date=task.due_date,
            tags=task.tags,
            description=task.description
        )
        await manager.broadcast_to_room(
            room_id=task.room_id,
            message={"type": "task_created", "task": dict(new_task)}
        )
        return new_task
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        print(f"Task data: {task.dict()}")
        raise HTTPException(status_code=422, detail=str(e))

@app.put("/tasks/{task_id}", response_model=Optional[Task])
async def update_task(task_id: int, task_update: TaskUpdate):
    # 只传递非None的字段
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    updated_task = await Database.update_task(task_id, **update_data)
    if updated_task:
        await manager.broadcast_to_room(
            room_id=updated_task.room_id,
            message={"type": "task_updated", "task": dict(updated_task)}
        )
    return updated_task

@app.patch("/tasks/{task_id}/toggle", response_model=Optional[Task])
async def toggle_task(task_id: int):
    """快速切换任务完成状态"""
    # 先获取当前任务状态
    task = await Database.get_task_by_id(task_id)
    if task:
        updated_task = await Database.update_task(task_id, completed=not task.completed)
        if updated_task:
            await manager.broadcast_to_room(
                room_id=updated_task.room_id,
                message={"type": "task_updated", "task": dict(updated_task)}
            )
        return updated_task
    return None

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, permanent: bool = False):
    """删除任务（默认软删除）"""
    # 获取任务信息用于广播
    task = await Database.get_task_by_id(task_id)
    if task:
        await Database.delete_task(task_id, soft_delete=not permanent)
        await manager.broadcast_to_room(
            room_id=task.room_id,
            message={"type": "task_deleted", "task_id": task_id, "permanent": permanent}
        )
    return {"status": "success"}

@app.get("/rooms/{room_id}/trash", response_model=List[Task])
async def get_trash_tasks(room_id: str):
    """获取垃圾桶中的任务"""
    return await Database.get_deleted_tasks(room_id)

@app.post("/tasks/{task_id}/restore")
async def restore_task(task_id: int):
    """从垃圾桶恢复任务"""
    task = await Database.get_task_by_id(task_id)
    if task:
        await Database.restore_task(task_id)
        restored_task = await Database.get_task_by_id(task_id)
        if restored_task:
            await manager.broadcast_to_room(
                room_id=restored_task.room_id,
                message={"type": "task_restored", "task": dict(restored_task)}
            )
        return {"status": "success"}
    return {"status": "not_found"}

# WebSocket连接
@app.websocket("/ws/{room_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_name: str):
    await manager.connect(websocket, room_id, user_name)
    try:
        room = await Database.get_room(room_id)
        if room:
            active_users = room.active_users + [user_name]
            await Database.update_room_users(room.id, active_users)
            await manager.broadcast_to_room(
                room_id=room_id,
                message={"type": "user_joined", "user_name": user_name}
            )
        
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_to_room(
                room_id=room_id,
                message={"type": "message", "user": user_name, "content": data}
            )
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_name)
        if room:
            active_users = [u for u in room.active_users if u != user_name]
            await Database.update_room_users(room.id, active_users)
            await manager.broadcast_to_room(
                room_id=room_id,
                message={"type": "user_left", "user_name": user_name}
            )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)