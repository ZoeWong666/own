# -*- coding: utf-8 -*-
"""
YOLOv8 训练系统 - 桌面客户端启动器
使用 pywebview 将 Web 应用封装为原生桌面应用
"""
import os
import sys
import threading
import time
from pathlib import Path

# 设置工作目录为可执行文件所在目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是源代码运行
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

# 导入必要的模块
import webview

# 导入主应用模块 (延迟导入,避免循环依赖)
def get_app():
    """延迟导入主应用"""
    import yolo_training_system
    return yolo_training_system.app

# 全局变量用于存储服务器状态
server_ready = False

def start_server():
    """在后台线程启动 Flask 服务器"""
    global server_ready
    try:
        print("正在启动 Flask 服务器...")
        # 使用无日志模式启动 Flask
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # 获取应用并启动服务器
        app = get_app()
        app.run(
            host='127.0.0.1',
            port=7865,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"服务器启动失败: {e}")

def main():
    """主函数"""
    print("=" * 70)
    print("🎯 YOLOv8 训练系统 - 桌面客户端")
    print("=" * 70)
    print()
    print("正在初始化...")

    # 在后台线程启动 Flask 服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)

    # 创建桌面窗口
    print("正在启动桌面客户端...")

    try:
        # 创建 pywebview 窗口
        window = webview.create_window(
            title='YOLOv8 训练系统',
            url='http://127.0.0.1:7865',
            width=1280,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600),
            confirm_close=True
        )

        print("✅ 桌面客户端已启动")
        print("=" * 70)

        # 启动 GUI (这会阻塞直到窗口关闭)
        webview.start(debug=False)

    except Exception as e:
        print(f"\n\n❌ 启动失败: {e}")
        print("\n请检查:")
        print("1. 端口 7865 是否被占用")
        print("2. 所有依赖是否已安装")
        input("\n按回车键退出...")

if __name__ == '__main__':
    main()
