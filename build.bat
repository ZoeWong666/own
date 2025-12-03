@echo off
REM YOLOv8 训练系统打包脚本 - Windows版本
chcp 65001 >nul

echo ╔══════════════════════════════════════════════════════════════════╗
echo ║        🚀 YOLOv8 训练系统 - 自动打包脚本 (Windows)             ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo ❌ 虚拟环境不存在
    echo 正在创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo ✓ 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装/更新 PyInstaller
echo.
echo ✓ 检查 PyInstaller...
pip install pyinstaller --upgrade -q

REM 清理旧的构建文件
echo.
echo ✓ 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 开始打包
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    开始打包，请稍候...                          ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

pyinstaller yolo_system.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║                    ✅ 打包成功！                                ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    echo 📦 可执行文件位置:
    echo    dist\YOLOv8训练系统\YOLOv8训练系统.exe
    echo.
    echo 📋 使用说明:
    echo    1. 进入 dist\YOLOv8训练系统\ 目录
    echo    2. 双击运行 'YOLOv8训练系统.exe'
    echo    3. 浏览器会自动打开 Web 界面
    echo.
    echo 💡 提示:
    echo    - 可以将整个 dist\YOLOv8训练系统\ 文件夹复制到其他电脑使用
    echo    - 首次运行可能需要几秒钟启动时间
    echo    - 如需关闭，在控制台按 Ctrl+C
    echo.

    REM 询问是否测试运行
    set /p test_choice="是否立即测试运行？(y/n): "
    if /i "%test_choice%"=="y" (
        echo.
        echo 启动应用...
        cd dist\YOLOv8训练系统\
        YOLOv8训练系统.exe
    )
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║                    ❌ 打包失败                                  ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    echo 请检查以上错误信息
    pause
    exit /b 1
)

pause
