#!/bin/bash

# Python-100天学习平台 - 本地开发停止脚本

echo "🛑 停止 Python-100天学习平台 - 本地开发服务"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 定义端口
BACKEND_PORT=8020
FRONTEND_PORT=9540

# 停止后端
echo "🐍 停止后端服务..."
if [ -f /tmp/python100days_backend.pid ]; then
    BACKEND_PID=$(cat /tmp/python100days_backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "   ${GREEN}✓${NC} 后端已停止 (PID: $BACKEND_PID)"
    else
        echo -e "   ${RED}✗${NC} 后端进程不存在"
    fi
    rm /tmp/python100days_backend.pid
else
    # 尝试通过端口查找并杀掉
    BACKEND_PID=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
    if [ -n "$BACKEND_PID" ]; then
        kill -9 $BACKEND_PID
        echo -e "   ${GREEN}✓${NC} 后端已停止 (PID: $BACKEND_PID)"
    else
        echo -e "   ${GREEN}✓${NC} 后端未运行"
    fi
fi

# 停止前端
echo "🎨 停止前端服务..."
if [ -f /tmp/python100days_frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/python100days_frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo -e "   ${GREEN}✓${NC} 前端已停止 (PID: $FRONTEND_PID)"
    else
        echo -e "   ${RED}✗${NC} 前端进程不存在"
    fi
    rm /tmp/python100days_frontend.pid
else
    # 尝试通过端口查找并杀掉
    FRONTEND_PID=$(lsof -ti:$FRONTEND_PORT 2>/dev/null || true)
    if [ -n "$FRONTEND_PID" ]; then
        kill -9 $FRONTEND_PID
        echo -e "   ${GREEN}✓${NC} 前端已停止 (PID: $FRONTEND_PID)"
    else
        echo -e "   ${GREEN}✓${NC} 前端未运行"
    fi
fi

echo ""
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo ""