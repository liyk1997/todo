# Todo应用 Docker 部署指南

本指南介绍如何将Todo应用（包含前端H5页面和Python后端API）打包到单个Docker容器中运行。

## 🏗️ 架构说明

- **前端**: H5静态页面，通过Nginx提供服务
- **后端**: Python FastAPI服务，提供REST API和WebSocket
- **数据库**: SQLite数据库文件
- **反向代理**: Nginx处理静态文件服务和API代理
- **进程管理**: Supervisor管理多个服务进程

## 📦 快速开始

### 方法一：使用 Docker Compose（推荐）

```bash
# 构建并启动容器
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法二：使用 Docker 命令

```bash
# 构建镜像
docker build -t todo-app .

# 运行容器
docker run -d \
  --name todo-fullstack \
  -p 80:80 \
  -p 8000:8000 \
  -v todo_data:/app/backend \
  todo-app

# 查看容器状态
docker ps

# 查看日志
docker logs -f todo-fullstack

# 停止容器
docker stop todo-fullstack
docker rm todo-fullstack
```

## 🌐 访问应用

启动成功后，可以通过以下方式访问：

- **前端应用**: http://localhost
- **后端API文档**: http://localhost:8000/docs
- **后端API**: http://localhost/api/

## 📁 项目结构

```
.
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker Compose配置
├── .dockerignore           # Docker忽略文件
├── docker/                 # Docker配置文件目录
│   ├── nginx.conf         # Nginx配置
│   ├── supervisord.conf   # Supervisor配置
│   └── start.sh           # 启动脚本
├── h5/                    # 前端H5应用
│   └── index.html
└── backend/               # 后端Python应用
    ├── main.py
    ├── requirements.txt
    └── ...
```

## 🔧 配置说明

### 端口映射
- `80:80` - Nginx前端服务端口
- `8000:8000` - 后端API服务端口（可选）

### 数据持久化
- 使用Docker卷 `todo_data` 持久化SQLite数据库文件
- 数据库文件位置：`/app/backend/todo.db`

### 环境变量
- `PYTHONPATH=/app/backend` - Python模块路径

## 🛠️ 开发和调试

### 查看容器内部
```bash
# 进入容器
docker exec -it todo-fullstack bash

# 查看进程状态
docker exec -it todo-fullstack supervisorctl status

# 重启服务
docker exec -it todo-fullstack supervisorctl restart backend
docker exec -it todo-fullstack supervisorctl restart nginx
```

### 查看日志
```bash
# 查看所有日志
docker logs todo-fullstack

# 查看Nginx日志
docker exec todo-fullstack tail -f /var/log/nginx.out.log

# 查看后端日志
docker exec todo-fullstack tail -f /var/log/backend.out.log
```

## 🚀 生产环境部署

### 安全建议
1. 修改默认端口
2. 配置HTTPS证书
3. 设置防火墙规则
4. 定期备份数据库

### 性能优化
1. 调整Nginx worker进程数
2. 配置适当的内存限制
3. 使用外部数据库（如PostgreSQL）

### 监控和维护
```bash
# 查看资源使用情况
docker stats todo-fullstack

# 备份数据
docker cp todo-fullstack:/app/backend/todo.db ./backup/

# 更新应用
docker-compose pull
docker-compose up -d
```

## ❓ 常见问题

**Q: 容器启动失败？**
A: 检查端口是否被占用，查看日志排查具体错误

**Q: 数据丢失？**
A: 确保使用了数据卷持久化，避免直接删除容器

**Q: 无法访问API？**
A: 检查Nginx配置和后端服务状态

**Q: 如何更新应用？**
A: 重新构建镜像并重启容器

## 📝 注意事项

1. 首次运行会自动初始化数据库
2. 数据库文件会持久化保存
3. 容器重启不会丢失数据
4. 建议在生产环境中使用外部数据库
5. 定期备份重要数据