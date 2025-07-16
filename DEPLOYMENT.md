# 部署指南

本文档提供了 Todo 应用的详细部署指南，支持多种部署方式。

## 🚀 快速部署

### 使用 Docker Compose（推荐）

这是最简单的部署方式，适合大多数用户：

```bash
# 克隆项目
git clone https://github.com/liyk1997/todo.git
cd todo

# 一键部署
docker-compose up -d
```

### 使用部署脚本

我们提供了自动化部署脚本：

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

## 📋 部署要求

### 系统要求
- **操作系统**: Linux, macOS, Windows
- **内存**: 最少 512MB，推荐 1GB+
- **存储**: 最少 1GB 可用空间
- **网络**: 需要访问互联网（用于拉取依赖）

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

## 🔧 详细部署步骤

### 1. 环境准备

#### 安装 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# macOS
brew install docker

# Windows
# 下载并安装 Docker Desktop
```

#### 安装 Docker Compose
```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# macOS/Windows
# Docker Desktop 已包含 Docker Compose
```

### 2. 获取源码

```bash
git clone https://github.com/liyk1997/todo.git
cd todo
```

### 3. 配置环境

#### 创建环境配置文件
```bash
cp backend/.env.example backend/.env
```

#### 编辑配置文件
```env
# backend/.env
DATABASE_URL=sqlite:///./todo.db
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost", "http://localhost:3000"]
```

### 4. 构建和启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 验证部署

访问以下地址验证部署：
- **前端应用**: http://localhost
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🌐 生产环境部署

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 使用 HTTPS

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 环境变量配置

生产环境建议使用环境变量：

```bash
# docker-compose.prod.yml
version: '3.8'
services:
  todo-app:
    build: .
    ports:
      - "80:80"
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_HOST=${API_HOST}
      - API_PORT=${API_PORT}
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - todo_data:/app/backend
    restart: unless-stopped
```

## 📊 监控和维护

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f todo-app

# 查看最近的日志
docker-compose logs --tail=100 -f
```

### 备份数据
```bash
# 备份数据库
docker-compose exec todo-app cp /app/backend/todo.db /app/backend/backup/

# 或者从宿主机备份
docker cp todo-fullstack:/app/backend/todo.db ./backup/
```

### 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
docker-compose down
docker-compose build
docker-compose up -d
```

### 性能优化
```bash
# 清理未使用的镜像
docker system prune -a

# 查看资源使用情况
docker stats

# 限制容器资源
# 在 docker-compose.yml 中添加:
# deploy:
#   resources:
#     limits:
#       memory: 512M
#       cpus: '0.5'
```

## 🔧 故障排除

### 常见问题

#### 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# 修改端口
# 编辑 docker-compose.yml 中的 ports 配置
```

#### 权限问题
```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

#### 内存不足
```bash
# 检查内存使用
free -h
docker stats

# 增加交换空间
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 调试模式

启用调试模式获取更多信息：

```bash
# 设置环境变量
export DEBUG=true

# 或在 docker-compose.yml 中添加
environment:
  - DEBUG=true
  - LOG_LEVEL=debug
```

## 📞 获取帮助

如果遇到部署问题：

1. 查看 [常见问题](https://github.com/liyk1997/todo/wiki/FAQ)
2. 搜索 [已知问题](https://github.com/liyk1997/todo/issues)
3. 提交 [新问题](https://github.com/liyk1997/todo/issues/new)
4. 参与 [讨论](https://github.com/liyk1997/todo/discussions)

## 📈 扩展部署

### 集群部署
- 使用 Docker Swarm 或 Kubernetes
- 配置负载均衡
- 设置数据库集群

### 云平台部署
- AWS ECS/EKS
- Google Cloud Run
- Azure Container Instances
- 阿里云容器服务

详细的云平台部署指南请参考相应的文档。