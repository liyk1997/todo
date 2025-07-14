# Todo List 后端服务

这是一个基于 FastAPI 和 WebSocket 的多人共享 Todo List 后端服务。

## 技术栈

- FastAPI：Web框架
- MongoDB：数据库
- WebSocket：实时通信
- Beanie：MongoDB ODM
- Pydantic：数据验证

## 功能特性

- 房间管理（创建/加入）
- 任务管理（创建/更新/删除）
- 实时数据同步
- 多用户协作
- WebSocket 实时通信

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置你的配置
```

3. 启动 MongoDB：
确保你的 MongoDB 服务已经启动。

4. 运行服务：
```bash
python main.py
```
服务将在 http://localhost:8000 启动。

## API 文档

启动服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要接口

1. 房间管理：
- POST `/api/rooms/create`：创建新房间
- POST `/api/rooms/join`：加入房间

2. 任务管理：
- GET `/api/tasks/{room_id}`：获取房间所有任务
- POST `/api/tasks`：创建新任务
- PUT `/api/tasks/{task_id}`：更新任务状态
- DELETE `/api/tasks/{task_id}`：删除任务

3. WebSocket：
- WebSocket `/ws/{room_id}`：实时通信连接

## WebSocket 事件

- `task_created`：新任务创建
- `task_updated`：任务状态更新
- `task_deleted`：任务被删除
- `user_joined`：新用户加入
- `user_left`：用户离开

## 开发说明

1. 数据模型在 `models.py` 中定义
2. WebSocket 管理器在 `websocket_manager.py` 中实现
3. 主要业务逻辑在 `main.py` 中实现

## 注意事项

1. 生产环境部署时请修改 CORS 设置
2. 确保 MongoDB 数据库的安全配置
3. 建议添加适当的请求频率限制
4. 根据需要调整 WebSocket 心跳检测机制