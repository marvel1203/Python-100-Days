#!/bin/bash

echo "🚀 启动 Python-100天学习平台开发环境"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行,请先启动Docker"
    exit 1
fi

# 创建.env文件(如果不存在)
if [ ! -f backend/.env ]; then
    echo "📝 创建后端环境配置文件..."
    cp backend/.env.example backend/.env
    echo "⚠️  请编辑 backend/.env 文件配置数据库密码等信息"
fi

# 构建并启动服务
echo "🔨 构建并启动所有服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 执行数据库迁移
echo "📊 执行数据库迁移..."
docker-compose exec -T backend python manage.py migrate

# 创建超级用户(可选)
echo ""
read -p "是否创建Django超级用户? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose exec backend python manage.py createsuperuser
fi

echo ""
echo "✅ 开发环境启动完成!"
echo ""
echo "📍 访问地址:"
echo "   前端应用: http://localhost:9540"
echo "   后端API: http://localhost:8020"
echo "   API文档: http://localhost:8020/swagger/"
echo "   Django管理后台: http://localhost:8020/admin/"
echo ""
echo "🛠️  常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
