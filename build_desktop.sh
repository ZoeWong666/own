#!/bin/bash
# YOLOv8训练系统 - 桌面客户端打包脚本

echo "========================================"
echo "YOLOv8 训练系统 - 桌面客户端打包"
echo "========================================"
echo ""

# 检查 Python 版本
echo "检查 Python 环境..."
python3 --version
echo ""

# 检查是否安装了 pywebview
echo "检查依赖..."
python3 -c "import webview; print('✓ pywebview 已安装')" || {
    echo "❌ pywebview 未安装，正在安装..."
    python3 -m pip install pywebview
}

# 检查是否安装了 PyInstaller
python3 -c "import PyInstaller; print('✓ PyInstaller 已安装')" || {
    echo "❌ PyInstaller 未安装，正在安装..."
    python3 -m pip install pyinstaller
}
echo ""

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf build dist
echo "✓ 清理完成"
echo ""

# 使用 PyInstaller 打包
echo "开始打包桌面客户端..."
echo "使用配置文件: desktop_system.spec"
echo ""

python3 -m PyInstaller desktop_system.spec --clean

# 检查打包结果
if [ -d "dist/YOLOv8训练系统" ]; then
    echo ""
    echo "========================================"
    echo "✅ 打包成功!"
    echo "========================================"
    echo ""
    echo "可执行文件位置:"
    echo "  dist/YOLOv8训练系统/YOLOv8训练系统"
    echo ""
    echo "运行方式:"
    echo "  1. 进入目录: cd dist/YOLOv8训练系统"
    echo "  2. 运行程序: ./YOLOv8训练系统"
    echo ""
    echo "或者直接双击 dist/YOLOv8训练系统/YOLOv8训练系统"
    echo ""

    # 创建 ZIP 归档
    echo "正在创建 ZIP 归档..."
    cd dist
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        ditto -c -k --sequesterRsrc --keepParent "YOLOv8训练系统" "YOLOv8训练系统-macOS.zip"
    else
        # Linux/Unix
        zip -r "YOLOv8训练系统-$(uname).zip" "YOLOv8训练系统"
    fi
    cd ..
    echo "✓ ZIP 归档创建完成: dist/YOLOv8训练系统-macOS.zip"
    echo ""
else
    echo ""
    echo "========================================"
    echo "❌ 打包失败"
    echo "========================================"
    echo ""
    echo "请检查错误信息"
    exit 1
fi
