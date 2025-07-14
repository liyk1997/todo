# 使用Python 3.10作为基础镜像
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
COPY backend/requirements.txt ./backend/

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制前端H5文件
COPY h5/ ./frontend/

# 配置Nginx
COPY docker/nginx.conf /etc/nginx/sites-available/default

# 配置Supervisor
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建启动脚本
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# 暴露端口
EXPOSE 80 8000

# 启动服务
CMD ["/start.sh"]