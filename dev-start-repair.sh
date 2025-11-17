#!/bin/bash
set -e

echo "开始修复并验证后端容器"

if ! docker info > /dev/null 2>&1; then
  echo "Docker未运行"
  exit 1
fi

docker compose up -d backend frontend
sleep 3

echo "覆盖容器内后端代码"
docker cp backend/config python100days_backend:/app/
docker cp backend/apps python100days_backend:/app/
docker cp backend/common python100days_backend:/app/
docker cp backend/manage.py python100days_backend:/app/manage.py

echo "清理容器内缓存"
docker exec python100days_backend sh -lc "find /app -name __pycache__ -type d -exec rm -rf {} +; find /app -name '*.pyc' -delete"

echo "重启后端容器"
docker restart python100days_backend
sleep 3

echo "导入课程数据"
docker exec python100days_backend python manage.py import_courses || true

echo "验证课程列表接口"
curl -s 'http://localhost:9540/api/courses/courses/?page=1&page_size=9' -i | head -n 30

echo "修复与验证完成"