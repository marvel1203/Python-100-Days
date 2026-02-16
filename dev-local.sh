#!/bin/bash

# Python-100天学习平台 - 本地开发启动脚本
# 功能: 清理端口、启动后端(热重载)、启动前端(热重载)

set -e

echo "🚀 启动 Python-100天学习平台 - 本地开发模式"
echo "================================================"
echo ""

# 定义端口
BACKEND_PORT=8020
FRONTEND_PORT=9540
MYSQL_PORT=3306
REDIS_PORT=6379

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数: 杀掉指定端口的进程
kill_port_process() {
    local port=$1
    local service_name=$2

    echo -n "🔍 检查端口 $port ($service_name)... "

    # 查找占用端口的进程
    local pid=$(lsof -ti:$port 2>/dev/null || true)

    if [ -n "$pid" ]; then
        echo -e "${YELLOW}发现进程 PID: $pid${NC}"
        echo -n "   正在终止进程... "

        # 杀掉进程
        kill -9 $pid 2>/dev/null || true
        sleep 1

        # 再次检查
        if lsof -ti:$port >/dev/null 2>&1; then
            echo -e "${RED}失败${NC}"
            return 1
        else
            echo -e "${GREEN}成功${NC}"
        fi
    else
        echo -e "${GREEN}空闲${NC}"
    fi
}

# 函数: 检查依赖
check_dependencies() {
    echo "📦 检查依赖..."

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
    echo -e "   ${GREEN}✓${NC} Python3: $(python3 --version)"

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    echo -e "   ${GREEN}✓${NC} Node.js: $(node --version)"

    # 检查 npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安装${NC}"
        exit 1
    fi
    echo -e "   ${GREEN}✓${NC} npm: $(npm --version)"

    echo ""
}

# 函数: 配置后端
setup_backend() {
    echo "🔧 配置后端环境..."

    cd backend

    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "   创建 Python 虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装依赖
    echo "   安装 Python 依赖..."
    pip install -q -r requirements.txt

    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        echo "   创建环境配置文件..."
        cp .env.example .env
        echo -e "   ${YELLOW}⚠️  请编辑 backend/.env 配置数据库密码${NC}"
    fi

    # 数据库迁移
    echo "   执行数据库迁移..."
    python manage.py migrate --noinput

    cd ..
    echo ""
}

# 函数: 配置前端
setup_frontend() {
    echo "🔧 配置前端环境..."

    cd frontend

    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo "   安装 Node.js 依赖..."
        npm install
    fi

    cd ..
    echo ""
}

# 函数: 启动后端
start_backend() {
    echo "🐍 启动后端服务 (Django + 热重载)..."
    echo "   端口: $BACKEND_PORT"

    cd backend
    source venv/bin/activate

    # 使用 Django 的 runserver 启动,自动支持热重载
    # --noreload 参数可以禁用热重载,这里不使用以保持热重载
    python manage.py runserver 0.0.0.0:$BACKEND_PORT &
    BACKEND_PID=$!

    echo -e "   ${GREEN}✓${NC} 后端已启动 (PID: $BACKEND_PID)"
    cd ..

    # 保存 PID 用于后续清理
    echo $BACKEND_PID > /tmp/python100days_backend.pid
    echo ""
}

# 函数: 启动前端
start_frontend() {
    echo "🎨 启动前端服务 (Vue 3 + Vite + 热重载)..."
    echo "   端口: $FRONTEND_PORT"

    cd frontend

    # Vite 默认支持热重载
    npm run dev &
    FRONTEND_PID=$!

    echo -e "   ${GREEN}✓${NC} 前端已启动 (PID: $FRONTEND_PID)"
    cd ..

    # 保存 PID 用于后续清理
    echo $FRONTEND_PID > /tmp/python100days_frontend.pid
    echo ""
}

# 函数: 显示访问信息
show_access_info() {
    echo "================================================"
    echo -e "${GREEN}✅ 开发环境启动完成!${NC}"
    echo "================================================"
    echo ""
    echo "📍 访问地址:"
    echo "   前端应用:     http://localhost:$FRONTEND_PORT"
    echo "   后端API:      http://localhost:$BACKEND_PORT"
    echo "   API文档:      http://localhost:$BACKEND_PORT/swagger/"
    echo "   Django管理后台: http://localhost:$BACKEND_PORT/admin/"
    echo ""
    echo "🔥 热重载已启用:"
    echo "   后端: 修改 Python 文件后自动重启"
    echo "   前端: 修改 Vue/JS/CSS 文件后自动刷新"
    echo ""
    echo "🛠️  常用命令:"
    echo "   查看后端日志: tail -f backend/logs/*.log"
    echo "   停止服务:     ./dev-stop-local.sh"
    echo "   重启服务:     ./dev-restart-local.sh"
    echo ""
    echo "💡 提示:"
    echo "   按 Ctrl+C 可停止所有服务"
    echo "   后端 PID: $BACKEND_PID"
    echo "   前端 PID: $FRONTEND_PID"
    echo ""
}

# 函数: 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."

    # 停止后端
    if [ -f /tmp/python100days_backend.pid ]; then
        BACKEND_PID=$(cat /tmp/python100days_backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm /tmp/python100days_backend.pid
        echo -e "   ${GREEN}✓${NC} 后端已停止"
    fi

    # 停止前端
    if [ -f /tmp/python100days_frontend.pid ]; then
        FRONTEND_PID=$(cat /tmp/python100days_frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm /tmp/python100days_frontend.pid
        echo -e "   ${GREEN}✓${NC} 前端已停止"
    fi

    echo ""
    echo "👋 开发环境已停止"
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 主流程
main() {
    # 清理端口
    echo "🧹 清理端口占用..."
    kill_port_process $BACKEND_PORT "后端API"
    kill_port_process $FRONTEND_PORT "前端应用"
    echo ""

    # 检查依赖
    check_dependencies

    # 配置环境
    setup_backend
    setup_frontend

    # 启动服务
    start_backend
    start_frontend

    # 显示访问信息
    show_access_info

    # 等待用户中断
    echo "⏳ 服务运行中... (按 Ctrl+C 停止)"
    wait
}

# 执行主流程
main