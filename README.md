# 📝 Todo - 多人协作任务管理系统
项目由trae ai 自动生成
一个基于 Vue3 + FastAPI 的现代化多人协作任务管理应用，支持实时同步、多平台部署。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.4.21-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-blue.svg)
![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)

## ✨ 功能特性

### 🎯 核心功能
- **多人协作**: 支持多用户实时协作，房间制管理
- **实时同步**: 基于 WebSocket 的实时数据同步
- **任务管理**: 创建、编辑、删除、完成任务
- **优先级管理**: 支持低、中、高、紧急四个优先级
- **截止日期**: 任务截止时间提醒
- **标签系统**: 灵活的任务标签分类
- **垃圾桶**: 软删除机制，支持任务恢复

### 🎨 用户体验
- **响应式设计**: 适配桌面端、平板、手机
- **现代化UI**: 简洁美观的用户界面
- **多平台支持**: 支持 H5、小程序、App 等多平台
- **实时反馈**: 操作即时反馈，流畅的用户体验

### 🔧 技术特性
- **前后端分离**: 清晰的架构设计
- **RESTful API**: 标准化的接口设计
- **数据持久化**: SQLite 数据库存储
- **容器化部署**: Docker 一键部署
- **负载均衡**: Nginx 反向代理

## 🛠️ 技术栈

### 前端技术
- **框架**: Vue 3.4.21 + TypeScript
- **构建工具**: Vite 5.2.8
- **跨平台**: uni-app (支持 H5、小程序、App)
- **样式**: SCSS + 响应式设计
- **状态管理**: Vue 3 Composition API

### 后端技术
- **框架**: FastAPI (Python)
- **数据库**: SQLite + aiosqlite
- **实时通信**: WebSocket
- **数据验证**: Pydantic
- **异步处理**: asyncio

### 部署技术
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **进程管理**: Supervisor
- **多阶段构建**: 优化镜像大小

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/liyk1997/todo.git
cd todo

# 使用 Docker Compose 一键启动
docker-compose up -d

# 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
```

### 方式二：本地开发

#### 前端开发
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build:h5
```

#### 后端开发
```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📱 多平台支持

### H5 网页版
```bash
npm run dev:h5          # 开发
npm run build:h5        # 构建
```

### 微信小程序
```bash
npm run dev:mp-weixin   # 开发
npm run build:mp-weixin # 构建
```

### App 应用
```bash
npm run dev:app         # 开发
npm run build:app       # 构建
```

## 🏗️ 项目结构

```
todo/
├── src/                    # 前端源码
│   ├── pages/             # 页面组件
│   ├── components/        # 公共组件
│   ├── api/              # API 接口
│   └── static/           # 静态资源
├── backend/               # 后端源码
│   ├── main.py           # FastAPI 主应用
│   ├── models.py         # 数据模型
│   ├── database.py       # 数据库操作
│   └── websocket_manager.py # WebSocket 管理
├── docker/               # Docker 配置
├── nginx.conf           # Nginx 配置
├── docker-compose.yml   # Docker Compose 配置
└── Dockerfile          # Docker 镜像构建
```

## 🔧 配置说明

### 环境变量
创建 `backend/.env` 文件：
```env
# 数据库配置
DATABASE_URL=sqlite:///./todo.db

# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 跨域配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost"]
```

### Nginx 配置
项目包含完整的 Nginx 配置，支持：
- 静态文件服务
- API 反向代理
- WebSocket 代理
- Gzip 压缩

## 📊 API 文档

启动后端服务后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口
- `GET /rooms/{room_id}/tasks` - 获取任务列表
- `POST /tasks` - 创建任务
- `PUT /tasks/{task_id}` - 更新任务
- `DELETE /tasks/{task_id}` - 删除任务
- `POST /tasks/{task_id}/restore` - 恢复任务
- `GET /rooms/{room_id}/trash` - 获取垃圾桶

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢以下开源项目：
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化 Python Web 框架
- [uni-app](https://uniapp.dcloud.io/) - 跨平台应用开发框架
- [Docker](https://www.docker.com/) - 容器化平台

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 [Issue](https://github.com/liyk1997/todo/issues)
- 发起 [Discussion](https://github.com/liyk1997/todo/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！
