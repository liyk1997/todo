#!/bin/bash

# 设置nginx文件权限
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# 初始化数据库
cd /app/backend
python init_db.py

# 启动supervisor管理的服务
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf