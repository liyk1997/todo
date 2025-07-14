@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 开始部署Todo应用...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查docker-compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 停止现有容器（如果存在）
echo 🛑 停止现有容器...
docker-compose down >nul 2>&1

REM 构建并启动容器
echo 🔨 构建Docker镜像...
docker-compose build
if errorlevel 1 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

echo ▶️  启动容器...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 容器启动失败
    pause
    exit /b 1
)

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

REM 显示访问信息
echo.
echo ✅ 部署完成！
echo 📱 前端应用: http://localhost
echo 🔧 后端API: http://localhost:8000/docs
echo 📋 查看日志: docker-compose logs -f
echo 🛑 停止服务: docker-compose down
echo.
echo 🎉 Todo应用已成功启动！
echo.
echo 按任意键退出...
pause >nul