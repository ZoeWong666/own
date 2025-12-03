#!/bin/bash
# YOLOv8 训练系统打包脚本
# 自动打包成可执行文件

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        🚀 YOLOv8 训练系统 - 自动打包脚本                        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在"
    echo "正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境（使用绝对路径）
echo "✓ 激活虚拟环境..."
VENV_BIN="venv/bin"

# 安装/更新 PyInstaller
echo ""
echo "✓ 检查 PyInstaller..."
$VENV_BIN/pip install pyinstaller --upgrade -q

# 清理旧的构建文件
echo ""
echo "✓ 清理旧的构建文件..."
rm -rf build/ dist/ *.spec.backup

# 开始打包
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    开始打包，请稍候...                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

$VENV_BIN/pyinstaller yolo_system.spec --clean

# 检查打包结果
if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ 打包成功！                                ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📦 可执行文件位置:"
    echo "   dist/YOLOv8训练系统/YOLOv8训练系统"
    echo ""
    echo "📋 使用说明:"
    echo "   1. 进入 dist/YOLOv8训练系统/ 目录"
    echo "   2. 双击运行 'YOLOv8训练系统' 可执行文件"
    echo "   3. 浏览器会自动打开 Web 界面"
    echo ""
    echo "💡 提示:"
    echo "   - 可以将整个 dist/YOLOv8训练系统/ 文件夹复制到其他电脑使用"
    echo "   - 首次运行可能需要几秒钟启动时间"
    echo "   - 如需关闭，在控制台按 Ctrl+C"
    echo ""

    # 显示文件大小
    echo "📊 打包信息:"
    du -sh dist/YOLOv8训练系统/
    echo ""
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    ❌ 打包失败                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "请检查以上错误信息"
    exit 1
fi

# 询问是否测试运行
echo ""
read -p "是否立即测试运行？(y/n): " test_choice
if [ "$test_choice" = "y" ]; then
    echo ""
    echo "启动应用..."
    cd dist/YOLOv8训练系统/
    ./YOLOv8训练系统
fi
