# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件
用于打包 YOLOv8 训练系统
"""
import glob
from pathlib import Path

block_cipher = None

# 需要收集的数据文件
datas = [
    ('yolov8n.pt', '.'),  # 预训练模型
]

# Collect trained models automatically
trained_models = glob.glob('yolo_workspace/models/**/weights/*.pt', recursive=True)
if trained_models:
    print(f"Found {len(trained_models)} trained models, packing them:")
    for model_path in trained_models:
        datas.append((model_path, str(Path(model_path).parent)))
        print(f"  - {model_path}")
else:
    print("No trained models found, packing default pretrained model only")

# 需要收集的隐藏导入
hiddenimports = [
    'flask',
    'werkzeug',
    'PIL',
    'cv2',
    'numpy',
    'ultralytics',
    'torch',
    'torchvision',
    'yaml',
    'pathlib',
    'json',
    'io',
    'glob',
    'datetime',
    'threading',
    'webbrowser',
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YOLOv8训练系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 显示控制台窗口，方便查看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加自定义图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YOLOv8训练系统',
)
