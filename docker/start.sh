#!/bin/bash

# 初始化数据库
cd /app/backend
python init_db.py

# 启动supervisor管理的服务
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf