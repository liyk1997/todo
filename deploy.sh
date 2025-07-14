#!/bin/bash

# Todo应用Docker部署脚本

set -e

echo "🚀 开始部署Todo应用..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 停止现有容器（如果存在）
echo "🛑 停止现有容器..."
docker-compose down 2>/dev/null || true

# 构建并启动容器
echo "🔨 构建Docker镜像..."
docker-compose build

echo "▶️  启动容器..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ 部署完成！"
echo "📱 前端应用: http://localhost"
echo "🔧 后端API: http://localhost:8000/docs"
echo "📋 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo ""
echo "🎉 Todo应用已成功启动！"