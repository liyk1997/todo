# Todo应用 Docker 部署指南

本指南介绍如何将Todo应用（包含Vue 3前端和Python后端API）打包到单个Docker容器中运行。

## 🏗️ 架构说明

- **前端**: Vue 3 + Vite 构建的单页应用，通过Nginx提供服务
- **后端**: Python FastAPI服务，提供REST API和WebSocket
- **数据库**: SQLite数据库文件
- **反向代理**: Nginx处理静态文件服务和API代理
- **进程管理**: Supervisor管理多个服务进程
- **构建方式**: 多阶段Docker构建，先构建前端再打包运行时环境

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
├── Dockerfile              # Docker镜像构建文件（多阶段构建）
├── docker-compose.yml      # Docker Compose配置
├── .dockerignore           # Docker忽略文件
├── docker/                 # Docker配置文件目录
│   ├── nginx.conf         # Nginx配置
│   ├── supervisord.conf   # Supervisor配置
│   └── start.sh           # 启动脚本
├── src/                   # Vue 3前端源码
│   ├── App.vue
│   ├── api/
│   ├── components/
│   ├── pages/
│   └── ...
├── package.json           # 前端依赖配置
├── vite.config.js         # Vite构建配置
├── nginx.conf             # Nginx配置文件
└── backend/               # 后端Python应用
    ├── main.py
    ├── requirements.txt
    └── ...
```

## 🔧 配置说明

### 多阶段构建
1. **第一阶段**: 使用Node.js镜像构建Vue 3前端应用
2. **第二阶段**: 使用Python镜像创建运行时环境，复制构建产物

### 端口映射
- `80:80` - Nginx前端服务端口
- `8000:8000` - 后端API服务端口（可选）

### 数据持久化
- 使用Docker卷 `todo_data` 持久化SQLite数据库文件
- 数据库文件位置：`/app/backend/todo.db`

### 环境变量
- `PYTHONPATH=/app/backend` - Python模块路径
- 前端自动根据环境选择API地址（开发环境：localhost:8000，生产环境：/api）

## 🛠️ 开发和调试

### 本地开发
```bash
# 安装前端依赖
npm install

# 启动前端开发服务器
npm run dev:h5

# 启动后端服务
cd backend
python main.py
```

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
docker exec todo-fullstack tail -f /var/log/nginx/access.log
docker exec todo-fullstack tail -f /var/log/nginx/error.log

# 查看后端日志
docker exec todo-fullstack tail -f /var/log/backend.out.log
```

## 🚀 CI/CD 部署

### GitHub Actions 自动构建
项目配置了GitHub Actions工作流，当代码推送到master分支时会自动：
1. 构建Docker镜像
2. 推送到Docker Hub

### 使用预构建镜像
```bash
# 拉取最新镜像
docker pull liyukang/todo:latest

# 运行预构建镜像
docker run -d \
  --name todo-fullstack \
  -p 80:80 \
  -p 8000:8000 \
  -v todo_data:/app/backend \
  liyukang/todo:latest
```

## 🔒 生产环境部署

### 安全建议
1. 修改默认端口
2. 配置HTTPS证书
3. 设置防火墙规则
4. 定期备份数据库
5. 使用环境变量管理敏感配置

### 性能优化
1. 调整Nginx worker进程数
2. 配置适当的内存限制
3. 使用外部数据库（如PostgreSQL）
4. 启用Gzip压缩
5. 配置静态资源缓存

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

**Q: 前端构建失败？**
A: 检查Node.js版本和依赖是否正确安装

**Q: 数据丢失？**
A: 确保使用了数据卷持久化，避免直接删除容器

**Q: 无法访问API？**
A: 检查Nginx配置和后端服务状态，确认API代理配置正确

**Q: 如何更新应用？**
A: 重新构建镜像并重启容器，或使用GitHub Actions自动部署

## 📝 注意事项

1. 首次运行会自动初始化数据库
2. 数据库文件会持久化保存
3. 容器重启不会丢失数据
4. 前端会根据环境自动选择API地址
5. 建议在生产环境中使用外部数据库
6. 定期备份重要数据
7. 多阶段构建可能需要更多时间，但镜像更小更安全