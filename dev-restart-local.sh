#!/bin/bash

# Python-100天学习平台 - 本地开发重启脚本

echo "🔄 重启 Python-100天学习平台 - 本地开发服务"
echo "================================================"
echo ""

# 停止服务
./dev-stop-local.sh

echo ""
echo "⏳ 等待 2 秒..."
sleep 2

echo ""
echo "🚀 重新启动服务..."
echo ""

# 启动服务
./dev-local.sh