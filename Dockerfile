# 多阶段构建
# 第一阶段：构建前端
FROM node:18-alpine as frontend-builder

WORKDIR /app

# 复制前端项目文件
COPY package*.json ./
COPY .npmrc ./
RUN npm ci

COPY src/ ./src/
COPY index.html ./
COPY vite.config.js ./
COPY jsconfig.json ./
COPY tsconfig.json ./

# 构建前端项目
RUN npm run build:h5

# 第二阶段：运行时环境
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码和依赖文件
COPY backend/ ./backend/

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/dist/ /var/www/html/

# 复制Nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 配置Supervisor
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建启动脚本
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# 暴露端口
EXPOSE 80 8000

# 启动服务
CMD ["/start.sh"]