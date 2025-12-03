#!/bin/bash
# 快速启动脚本

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🎯 YOLOv8 训练系统 - 快速启动菜单                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在"
    echo ""
    read -p "是否创建虚拟环境并安装依赖？(y/n): " install_choice
    if [ "$install_choice" = "y" ]; then
        echo "正在创建虚拟环境..."
        python3 -m venv venv
        echo "正在激活虚拟环境..."
        source venv/bin/activate
        echo "正在安装依赖..."
        pip install -r requirements.txt
        echo "✓ 安装完成！"
        echo ""
    else
        echo "已取消"
        exit 0
    fi
else
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
fi

echo ""
echo "请选择要启动的功能:"
echo ""
echo "  1. 🎯 训练系统 - 专业版（推荐）"
echo "     完整训练流程 + 20+参数 + 模型选择"
echo "     端口: 7865"
echo ""
echo "  2. 🎯 训练系统 - 基础版"
echo "     简化版训练界面"
echo "     端口: 7864"
echo ""
echo "  3. 🔍 简洁检测界面"
echo "     只做检测，不含训练"
echo "     端口: 7863"
echo ""
echo "  4. 🔌 REST API 服务器"
echo "     提供检测API接口"
echo "     端口: 8000"
echo ""
echo "  5. 📦 安装/更新依赖"
echo ""
echo "  0. 退出"
echo ""
read -p "请输入选项 (0-5): " choice

case $choice in
    1)
        echo ""
        echo "正在启动专业版训练系统..."
        echo "浏览器访问: http://localhost:7865"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python yolo_training_system_v2.py
        ;;
    2)
        echo ""
        echo "正在启动基础版训练系统..."
        echo "浏览器访问: http://localhost:7864"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python yolo_training_system.py
        ;;
    3)
        echo ""
        echo "正在启动简洁检测界面..."
        echo "浏览器访问: http://localhost:7863"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python simple_web_app.py
        ;;
    4)
        echo ""
        echo "正在启动 API 服务器..."
        echo "API 文档: http://localhost:8000/docs"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python detection_api.py
        ;;
    5)
        echo ""
        echo "正在更新依赖..."
        pip install -r requirements.txt --upgrade
        echo "✓ 更新完成"
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
