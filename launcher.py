# -*- coding: utf-8 -*-
"""
YOLOv8 训练系统 - 启动器
自动启动 Flask 服务并打开浏览器
"""
import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# 设置工作目录为可执行文件所在目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是源代码运行
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

# 导入主应用
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import json
import glob
import yaml
from PIL import Image
import io
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime

# 导入主应用模块
import yolo_training_system

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://localhost:7865')
    print("\n✅ 浏览器已自动打开")
    print("如果浏览器未打开，请手动访问: http://localhost:7865\n")

def main():
    """主函数"""
    print("=" * 70)
    print("🎯 YOLOv8 训练系统 - 启动中...")
    print("=" * 70)
    print()

    # 在新线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # 启动 Flask 应用
    try:
        yolo_training_system.app.run(
            host='0.0.0.0',
            port=7865,
            debug=False
        )
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n\n❌ 启动失败: {e}")
        print("\n请检查:")
        print("1. 端口 7865 是否被占用")
        print("2. 所有依赖是否已安装")
        input("\n按回车键退出...")

if __name__ == '__main__':
    main()
