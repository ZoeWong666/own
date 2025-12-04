# -*- coding: utf-8 -*-
"""
YOLOv8 完整训练系统 V2 - 包含标注、训练、测试功能
新增：模型选择、更多训练参数
"""
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
import glob
from pathlib import Path
import yaml
from PIL import Image
import io
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB限制

# 工作目录
WORKSPACE = Path('yolo_workspace')
WORKSPACE.mkdir(exist_ok=True)

# 数据集配置文件
DATASET_CONFIG_FILE = WORKSPACE / 'dataset_config.json'

def load_dataset_config():
    """加载数据集配置"""
    if DATASET_CONFIG_FILE.exists():
        with open(DATASET_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return Path(config.get('dataset_path', str(WORKSPACE / 'dataset')))
    return WORKSPACE / 'dataset'

def save_dataset_config(dataset_path):
    """保存数据集配置"""
    with open(DATASET_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({'dataset_path': str(dataset_path)}, f, ensure_ascii=False, indent=2)

# 数据集目录
DATASET_DIR = load_dataset_config()

def ensure_dataset_structure(dataset_dir):
    """确保数据集目录结构存在"""
    dataset_dir = Path(dataset_dir)
    dataset_dir.mkdir(exist_ok=True)
    (dataset_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    return dataset_dir

ensure_dataset_structure(DATASET_DIR)

# 训练模型保存目录
MODELS_DIR = WORKSPACE / 'models'
MODELS_DIR.mkdir(exist_ok=True)

# 加载类别配置
CLASSES_FILE = WORKSPACE / 'classes.json'

def load_classes():
    """加载类别配置"""
    if CLASSES_FILE.exists():
        with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_classes(classes):
    """保存类别配置"""
    with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(classes, f, ensure_ascii=False, indent=2)

def get_available_models():
    """获取所有可用的模型"""
    models = []

    # 预训练模型
    pretrained = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
    for model in pretrained:
        if Path(model).exists():
            models.append({
                'path': model,
                'name': f'预训练-{model}',
                'type': 'pretrained'
            })

    # 自定义训练的模型
    custom_models = glob.glob(str(MODELS_DIR / '**' / 'weights' / '*.pt'), recursive=True)
    for model_path in custom_models:
        rel_path = Path(model_path).relative_to(MODELS_DIR.parent)
        model_name = Path(model_path).parent.parent.name
        models.append({
            'path': str(model_path),
            'name': f'自定义-{model_name}',
            'type': 'custom'
        })

    return models

@app.route('/')
def index():
    """主页"""
    classes = load_classes()

    # 统计数据
    train_images = list((DATASET_DIR / 'images' / 'train').glob('*.*'))
    val_images = list((DATASET_DIR / 'images' / 'val').glob('*.*'))
    train_labels = list((DATASET_DIR / 'labels' / 'train').glob('*.txt'))
    val_labels = list((DATASET_DIR / 'labels' / 'val').glob('*.txt'))

    stats = {
        'classes': len(classes),
        'train_images': len(train_images),
        'train_labeled': len(train_labels),
        'val_images': len(val_images),
        'val_labeled': len(val_labels)
    }

    available_models = get_available_models()

    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YOLOv8 训练系统 V2</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}

        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }}

        .tabs {{
            display: flex;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}

        .tab {{
            padding: 15px 30px;
            cursor: pointer;
            background: none;
            border: none;
            font-size: 1.1em;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}

        .tab:hover {{
            color: #667eea;
        }}

        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .section {{
            background: #f8f9ff;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}

        .section-title {{
            font-size: 1.3em;
            color: #333;
            margin-bottom: 15px;
            font-weight: bold;
        }}

        .btn {{
            padding: 12px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
        }}

        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .btn-secondary {{
            background: linear-gradient(45deg, #48c6ef 0%, #6f86d6 100%);
        }}

        input[type="text"], input[type="number"], select {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 15px;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        label {{
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }}

        .help-text {{
            font-size: 0.85em;
            color: #666;
            margin-top: -10px;
            margin-bottom: 15px;
        }}

        .info-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .warning-box {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .success-box {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .path-box {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            margin: 10px 0;
            border: 1px solid #ddd;
            font-size: 0.9em;
        }}

        .class-list {{
            list-style: none;
            padding: 0;
        }}

        .class-item {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .class-name {{
            font-size: 1.1em;
            color: #333;
        }}

        .class-id {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}

        #annotationCanvas {{
            border: 2px solid #667eea;
            border-radius: 8px;
            cursor: crosshair;
            max-width: 100%;
            background: #f0f0f0;
        }}

        .btn-group {{
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }}

        .training-output {{
            background: #1e1e1e;
            color: #00ff00;
            padding: 20px;
            border-radius: 8px;
            font-family: monospace;
            max-height: 400px;
            overflow-y: auto;
            margin: 20px 0;
        }}

        .param-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .param-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 YOLOv8 训练系统 V2</h1>
        <p class="subtitle">数据标注 → 模型训练 → 效果测试 | 专业版</p>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{stats['classes']}</div>
                <div class="stat-label">类别数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['train_images']}</div>
                <div class="stat-label">训练图片</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['train_labeled']}</div>
                <div class="stat-label">已标注(训练)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['val_images']}</div>
                <div class="stat-label">验证图片</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['val_labeled']}</div>
                <div class="stat-label">已标注(验证)</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('classes')">1. 设置类别</button>
            <button class="tab" onclick="switchTab('annotate')">2. 标注数据</button>
            <button class="tab" onclick="switchTab('train')">3. 开始训练</button>
            <button class="tab" onclick="switchTab('test')">4. 测试模型</button>
        </div>

        <!-- 标签页1: 设置类别 -->
        <div id="classes-tab" class="tab-content active">
            <div class="section">
                <div class="section-title">⚙️ 数据集配置</div>
                <div class="warning-box">
                    <strong>💾 数据集路径设置:</strong> 可以自定义数据集保存位置
                </div>
                <div class="form-group">
                    <label>数据集保存路径</label>
                    <input type="text" id="datasetPath" value="{DATASET_DIR.absolute()}" placeholder="输入数据集绝对路径">
                    <button class="btn btn-secondary" onclick="updateDatasetPath()" style="margin-top: 10px;">💾 更新路径</button>
                </div>
            </div>
            <div class="section">
                <div class="section-title">📝 定义检测类别</div>
                <div class="info-box">
                    <strong>💡 提示:</strong> 先定义你要检测的物体类别，例如：person, car, dog, cat, chair
                </div>
                <div class="form-group">
                    <label>输入类别名称（中文或英文）</label>
                    <input type="text" id="classInput" placeholder="例如: person, car, dog" onkeypress="if(event.key==='Enter')addClass()">
                </div>
                <button class="btn" onclick="addClass()">➕ 添加类别</button>
                <div style="margin-top: 30px;">
                    <div class="section-title">当前类别列表</div>
                    <ul class="class-list" id="classList">
                        {''.join([f'<li class="class-item"><span class="class-name">{cls}</span><span class="class-id">ID: {i}</span></li>' for i, cls in enumerate(classes)])}
                    </ul>
                </div>
                <div class="path-box">
                    <strong>📁 数据集路径:</strong><br>
                    {DATASET_DIR.absolute()}
                </div>
            </div>
        </div>

        <!-- 标签页2: 标注数据 -->
        <div id="annotate-tab" class="tab-content">
            <div class="section">
                <div class="section-title">🖼️ 图片标注</div>
                <div class="info-box">
                    <strong>💡 使用说明:</strong>
                    <ol style="margin-left: 20px; margin-top: 10px;">
                        <li>选择图片文件夹批量导入，或单独上传图片</li>
                        <li>在图片上拖动鼠标框选物体</li>
                        <li>选择物体类别并保存</li>
                        <li>自动跳转到下一张未标注图片</li>
                    </ol>
                </div>
                <div class="form-group">
                    <label>选择数据集类型</label>
                    <select id="datasetType">
                        <option value="train">训练集 (80%图片)</option>
                        <option value="val">验证集 (20%图片)</option>
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>方式1: 选择图片文件夹（推荐）</label>
                        <input type="text" id="folderPath" placeholder="输入文件夹绝对路径">
                        <button class="btn btn-secondary" onclick="loadFolderImages()" style="margin-top: 10px;">📁 加载文件夹</button>
                    </div>
                    <div class="form-group">
                        <label>方式2: 单独上传图片</label>
                        <input type="file" id="imageUpload" accept="image/*" onchange="loadSingleImage()">
                    </div>
                </div>
                <div id="imageListContainer" style="display: none; margin: 20px 0;">
                    <div class="section-title">图片列表 (<span id="imageCount">0</span> 张)</div>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <button class="btn btn-secondary" onclick="previousImage()">⬅️ 上一张</button>
                        <button class="btn btn-secondary" onclick="nextImage()">下一张 ➡️</button>
                        <span style="line-height: 45px; margin-left: 10px;">
                            当前: <strong id="currentImageIndex">0</strong> / <strong id="totalImages">0</strong>
                            <span id="labeledStatus" style="margin-left: 10px;"></span>
                        </span>
                    </div>
                </div>
                <div class="canvas-container">
                    <canvas id="annotationCanvas" width="800" height="600"></canvas>
                </div>
                <div class="btn-group">
                    <button class="btn btn-secondary" onclick="clearAnnotations()">🗑️ 清除标注</button>
                    <button class="btn" onclick="saveAnnotations()">💾 保存标注</button>
                </div>
                <div class="path-box">
                    <strong>📁 图片保存位置:</strong><br>
                    训练集: {(DATASET_DIR / 'images' / 'train').absolute()}<br>
                    验证集: {(DATASET_DIR / 'images' / 'val').absolute()}<br><br>
                    <strong>📄 标注文件位置:</strong><br>
                    训练集: {(DATASET_DIR / 'labels' / 'train').absolute()}<br>
                    验证集: {(DATASET_DIR / 'labels' / 'val').absolute()}
                </div>
            </div>
        </div>

        <!-- 标签页3: 开始训练 -->
        <div id="train-tab" class="tab-content">
            <div class="section">
                <div class="section-title">🚀 模型训练 - 高级参数</div>
                <div class="warning-box">
                    <strong>⚠️ 训练前检查:</strong>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>已定义类别: {len(classes)} 个</li>
                        <li>训练集图片: {stats['train_images']} 张（已标注: {stats['train_labeled']}）</li>
                        <li>验证集图片: {stats['val_images']} 张（已标注: {stats['val_labeled']}）</li>
                        <li>建议每个类别至少100张标注图片</li>
                    </ul>
                </div>

                <!-- 基础参数 -->
                <div class="param-card">
                    <h3>🎯 基础参数</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>模型大小</label>
                            <select id="modelSize">
                                <option value="yolov8n.pt">Nano - 最快 (3.2M参数)</option>
                                <option value="yolov8s.pt">Small - 平衡 (11.2M参数)</option>
                                <option value="yolov8m.pt">Medium - 高精度 (25.9M参数)</option>
                                <option value="yolov8l.pt">Large - 更高精度 (43.7M参数)</option>
                                <option value="yolov8x.pt">XLarge - 最高精度 (68.2M参数)</option>
                            </select>
                            <div class="help-text">建议：实时检测用Nano，高精度用Large</div>
                        </div>
                        <div class="form-group">
                            <label>训练轮数 (Epochs)</label>
                            <input type="number" id="epochs" value="100" min="1" max="1000">
                            <div class="help-text">建议：100-300轮，数据少用更多轮数</div>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>批次大小 (Batch Size)</label>
                            <input type="number" id="batchSize" value="16" min="1" max="128">
                            <div class="help-text">建议：16-32，显存不足时减小</div>
                        </div>
                        <div class="form-group">
                            <label>图片大小 (Image Size)</label>
                            <input type="number" id="imgSize" value="640" min="320" max="1280" step="32">
                            <div class="help-text">建议：640标准，1280高精度</div>
                        </div>
                    </div>
                </div>

                <!-- 优化器参数 -->
                <div class="param-card">
                    <h3>⚙️ 优化器参数</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>学习率 (Learning Rate)</label>
                            <input type="number" id="lr" value="0.01" min="0.0001" max="0.1" step="0.001">
                            <div class="help-text">默认：0.01，数据少时可减小到0.001</div>
                        </div>
                        <div class="form-group">
                            <label>动量 (Momentum)</label>
                            <input type="number" id="momentum" value="0.937" min="0.5" max="0.999" step="0.001">
                            <div class="help-text">默认：0.937</div>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>权重衰减 (Weight Decay)</label>
                            <input type="number" id="weightDecay" value="0.0005" min="0" max="0.01" step="0.0001">
                            <div class="help-text">防止过拟合，默认：0.0005</div>
                        </div>
                        <div class="form-group">
                            <label>预热轮数 (Warmup Epochs)</label>
                            <input type="number" id="warmupEpochs" value="3" min="0" max="10">
                            <div class="help-text">学习率预热，默认：3轮</div>
                        </div>
                    </div>
                </div>

                <!-- 数据增强 -->
                <div class="param-card">
                    <h3>🎨 数据增强</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>色调偏移 (HSV-H)</label>
                            <input type="number" id="hsvH" value="0.015" min="0" max="0.1" step="0.001">
                            <div class="help-text">颜色变化，默认：0.015</div>
                        </div>
                        <div class="form-group">
                            <label>饱和度偏移 (HSV-S)</label>
                            <input type="number" id="hsvS" value="0.7" min="0" max="1" step="0.1">
                            <div class="help-text">饱和度变化，默认：0.7</div>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>亮度偏移 (HSV-V)</label>
                            <input type="number" id="hsvV" value="0.4" min="0" max="1" step="0.1">
                            <div class="help-text">亮度变化，默认：0.4</div>
                        </div>
                        <div class="form-group">
                            <label>旋转角度 (Degrees)</label>
                            <input type="number" id="degrees" value="0" min="0" max="45">
                            <div class="help-text">随机旋转，0表示不旋转</div>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>翻转概率 (Flip LR)</label>
                            <input type="number" id="flipLr" value="0.5" min="0" max="1" step="0.1">
                            <div class="help-text">左右翻转概率，默认：0.5</div>
                        </div>
                        <div class="form-group">
                            <label>马赛克增强</label>
                            <input type="number" id="mosaic" value="1.0" min="0" max="1" step="0.1">
                            <div class="help-text">拼接4张图，默认：1.0开启</div>
                        </div>
                    </div>
                </div>

                <!-- 其他参数 -->
                <div class="param-card">
                    <h3>🔧 其他参数</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>早停耐心值 (Patience)</label>
                            <input type="number" id="patience" value="50" min="0" max="100">
                            <div class="help-text">多少轮无提升则停止，0表示不早停</div>
                        </div>
                        <div class="form-group">
                            <label>置信度阈值 (Confidence)</label>
                            <input type="number" id="confThresh" value="0.25" min="0" max="1" step="0.05">
                            <div class="help-text">预测时的置信度阈值</div>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>IoU阈值</label>
                            <input type="number" id="iouThresh" value="0.7" min="0" max="1" step="0.05">
                            <div class="help-text">NMS IoU阈值</div>
                        </div>
                        <div class="form-group">
                            <label>工作线程数 (Workers)</label>
                            <input type="number" id="workers" value="8" min="0" max="16">
                            <div class="help-text">数据加载线程数，默认：8</div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>实验名称</label>
                        <input type="text" id="projectName" value="custom_model" placeholder="给你的模型起个名字">
                        <div class="help-text">模型将保存在: models/runs/detect/实验名称/</div>
                    </div>
                </div>

                <button class="btn" onclick="startTraining()" style="width: 100%; font-size: 1.3em; padding: 18px;">
                    🎯 开始训练
                </button>

                <div id="trainingOutput" class="training-output" style="display:none;">
                    训练日志将显示在这里...
                </div>

                <div class="path-box">
                    <strong>💾 模型保存位置:</strong><br>
                    {MODELS_DIR.absolute()}/runs/detect/[实验名称]/weights/best.pt
                </div>
            </div>
        </div>

        <!-- 标签页4: 测试模型 -->
        <div id="test-tab" class="tab-content">
            <div class="section">
                <div class="section-title">🧪 测试模型</div>
                <div class="info-box">
                    <strong>💡 提示:</strong> 选择模型并上传图片测试检测效果
                </div>

                <div class="form-group">
                    <label>选择测试模型</label>
                    <select id="testModelSelect">
                        <option value="">请选择模型...</option>
                        {''.join([f'<option value="{m["path"]}">{m["name"]}</option>' for m in available_models])}
                    </select>
                    <div class="help-text">
                        可用模型: {len(available_models)} 个
                        {'(包含预训练模型和自定义训练模型)' if available_models else '(暂无可用模型，请先训练或下载预训练模型)'}
                    </div>
                </div>

                <div class="form-group">
                    <label>上传测试图片</label>
                    <input type="file" id="testImage" accept="image/*">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>置信度阈值</label>
                        <input type="number" id="testConf" value="0.25" min="0" max="1" step="0.05">
                        <div class="help-text">只显示置信度高于此值的检测结果</div>
                    </div>
                    <div class="form-group">
                        <label>IoU阈值 (NMS)</label>
                        <input type="number" id="testIou" value="0.45" min="0" max="1" step="0.05">
                        <div class="help-text">去重时的IoU阈值</div>
                    </div>
                </div>

                <button class="btn" onclick="testModel()" style="width: 100%;">🔍 开始检测</button>

                <div id="testResult" style="margin-top: 20px;"></div>
                <div id="testInfo" style="margin-top: 10px;"></div>

                <div class="path-box">
                    <strong>📂 可用模型位置:</strong><br>
                    • 预训练模型: 当前目录/yolov8*.pt<br>
                    • 自定义模型: {MODELS_DIR.absolute()}/runs/detect/*/weights/*.pt
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentClasses = {json.dumps(classes)};
        let annotations = [];
        let canvas = null;
        let ctx = null;
        let currentImage = null;
        let isDrawing = false;
        let startX, startY;
        let imageList = [];
        let currentImageIdx = -1;
        let isFolderMode = false;

        function switchTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }}

        async function addClass() {{
            const input = document.getElementById('classInput');
            const className = input.value.trim();
            if (!className) {{
                alert('请输入类别名称');
                return;
            }}
            const response = await fetch('/api/classes', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{name: className}})
            }});
            if (response.ok) {{
                const data = await response.json();
                currentClasses = data.classes;
                updateClassList();
                input.value = '';
            }}
        }}

        function updateClassList() {{
            const listHtml = currentClasses.map((cls, i) =>
                `<li class="class-item">
                    <span class="class-name">${{cls}}</span>
                    <span class="class-id">ID: ${{i}}</span>
                </li>`
            ).join('');
            document.getElementById('classList').innerHTML = listHtml;
        }}

        async function updateDatasetPath() {{
            const path = document.getElementById('datasetPath').value.trim();
            if (!path) {{
                alert('请输入数据集路径');
                return;
            }}
            const response = await fetch('/api/dataset-path', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{path: path}})
            }});
            if (response.ok) {{
                const data = await response.json();
                alert('数据集路径已更新: ' + data.dataset_path);
                location.reload();
            }} else {{
                alert('更新失败');
            }}
        }}

        async function loadFolderImages() {{
            const folderPath = document.getElementById('folderPath').value.trim();
            if (!folderPath) {{
                alert('请输入文件夹路径');
                return;
            }}
            const datasetType = document.getElementById('datasetType').value;
            const response = await fetch('/api/folder-images', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    folder_path: folderPath,
                    dataset_type: datasetType
                }})
            }});
            if (response.ok) {{
                const data = await response.json();
                imageList = data.images;
                isFolderMode = true;
                document.getElementById('imageListContainer').style.display = 'block';
                document.getElementById('imageCount').textContent = data.total;
                document.getElementById('totalImages').textContent = data.total;

                // 自动跳转到第一张未标注的图片
                const firstUnlabeled = imageList.findIndex(img => !img.labeled);
                currentImageIdx = firstUnlabeled >= 0 ? firstUnlabeled : 0;
                loadImageAtIndex(currentImageIdx);
            }} else {{
                alert('加载文件夹失败');
            }}
        }}

        function loadImageAtIndex(idx) {{
            if (idx < 0 || idx >= imageList.length) return;
            currentImageIdx = idx;
            const imageInfo = imageList[idx];

            // 更新UI
            document.getElementById('currentImageIndex').textContent = idx + 1;
            const statusEl = document.getElementById('labeledStatus');
            if (imageInfo.labeled) {{
                statusEl.innerHTML = '<span style="color: green;">✓ 已标注</span>';
            }} else {{
                statusEl.innerHTML = '<span style="color: orange;">⚠ 未标注</span>';
            }}

            // 通过 API 加载图片
            fetch('/api/load-image', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{path: imageInfo.path}})
            }})
                .then(res => res.blob())
                .then(blob => {{
                    const reader = new FileReader();
                    reader.onload = function(e) {{
                        const img = new Image();
                        img.onload = function() {{
                            canvas = document.getElementById('annotationCanvas');
                            ctx = canvas.getContext('2d');
                            const maxWidth = 800;
                            const maxHeight = 600;
                            let width = img.width;
                            let height = img.height;
                            if (width > maxWidth) {{
                                height = height * (maxWidth / width);
                                width = maxWidth;
                            }}
                            if (height > maxHeight) {{
                                width = width * (maxHeight / height);
                                height = maxHeight;
                            }}
                            canvas.width = width;
                            canvas.height = height;
                            ctx.drawImage(img, 0, 0, width, height);
                            currentImage = img;
                            annotations = [];
                            canvas.onmousedown = startDrawing;
                            canvas.onmousemove = draw;
                            canvas.onmouseup = stopDrawing;
                        }};
                        img.src = e.target.result;
                    }};
                    reader.readAsDataURL(blob);
                }})
                .catch(err => {{
                    alert('加载图片失败: ' + err);
                }});
        }}

        function nextImage() {{
            if (currentImageIdx < imageList.length - 1) {{
                loadImageAtIndex(currentImageIdx + 1);
            }} else {{
                alert('已经是最后一张图片了');
            }}
        }}

        function previousImage() {{
            if (currentImageIdx > 0) {{
                loadImageAtIndex(currentImageIdx - 1);
            }} else {{
                alert('已经是第一张图片了');
            }}
        }}

        function loadSingleImage() {{
            isFolderMode = false;
            document.getElementById('imageListContainer').style.display = 'none';
            loadImage();
        }}

        function loadImage() {{
            const file = document.getElementById('imageUpload').files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {{
                const img = new Image();
                img.onload = function() {{
                    canvas = document.getElementById('annotationCanvas');
                    ctx = canvas.getContext('2d');
                    const maxWidth = 800;
                    const maxHeight = 600;
                    let width = img.width;
                    let height = img.height;
                    if (width > maxWidth) {{
                        height = height * (maxWidth / width);
                        width = maxWidth;
                    }}
                    if (height > maxHeight) {{
                        width = width * (maxHeight / height);
                        height = maxHeight;
                    }}
                    canvas.width = width;
                    canvas.height = height;
                    ctx.drawImage(img, 0, 0, width, height);
                    currentImage = img;
                    canvas.onmousedown = startDrawing;
                    canvas.onmousemove = draw;
                    canvas.onmouseup = stopDrawing;
                }};
                img.src = e.target.result;
            }};
            reader.readAsDataURL(file);
        }}

        function startDrawing(e) {{
            isDrawing = true;
            const rect = canvas.getBoundingClientRect();
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
        }}

        function draw(e) {{
            if (!isDrawing) return;
            const rect = canvas.getBoundingClientRect();
            const currentX = e.clientX - rect.left;
            const currentY = e.clientY - rect.top;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#00ff00';
            ctx.lineWidth = 2;
            ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
        }}

        function stopDrawing(e) {{
            if (!isDrawing) return;
            isDrawing = false;
            const rect = canvas.getBoundingClientRect();
            const endX = e.clientX - rect.left;
            const endY = e.clientY - rect.top;
            const classId = prompt('请输入类别ID (0-' + (currentClasses.length-1) + '):\\n' +
                currentClasses.map((c, i) => i + ': ' + c).join('\\n'));
            if (classId !== null) {{
                annotations.push({{
                    classId: parseInt(classId),
                    x: startX,
                    y: startY,
                    width: endX - startX,
                    height: endY - startY
                }});
                drawAllAnnotations();
            }}
        }}

        function drawAllAnnotations() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);
            annotations.forEach(ann => {{
                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.strokeRect(ann.x, ann.y, ann.width, ann.height);
                ctx.fillStyle = '#00ff00';
                ctx.font = '14px Arial';
                ctx.fillText(currentClasses[ann.classId], ann.x, ann.y - 5);
            }});
        }}

        function clearAnnotations() {{
            annotations = [];
            if (currentImage) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);
            }}
        }}

        async function saveAnnotations() {{
            if (annotations.length === 0) {{
                alert('请先标注物体');
                return;
            }}

            const datasetType = document.getElementById('datasetType').value;
            const formData = new FormData();

            if (isFolderMode) {{
                // 文件夹模式：通过 API 读取文件
                const currentImageInfo = imageList[currentImageIdx];
                const response = await fetch('/api/load-image', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{path: currentImageInfo.path}})
                }});
                const blob = await response.blob();
                formData.append('image', blob, currentImageInfo.name);
            }} else {{
                // 单文件模式
                const file = document.getElementById('imageUpload').files[0];
                formData.append('image', file);
            }}

            formData.append('dataset_type', datasetType);
            formData.append('annotations', JSON.stringify(annotations));
            formData.append('image_width', canvas.width);
            formData.append('image_height', canvas.height);

            const saveResponse = await fetch('/api/save-annotation', {{
                method: 'POST',
                body: formData
            }});

            if (saveResponse.ok) {{
                alert('标注保存成功！');
                annotations = [];

                if (isFolderMode) {{
                    // 更新当前图片的标注状态
                    imageList[currentImageIdx].labeled = true;

                    // 自动跳转到下一张未标注的图片
                    let nextUnlabeledIdx = -1;
                    for (let i = currentImageIdx + 1; i < imageList.length; i++) {{
                        if (!imageList[i].labeled) {{
                            nextUnlabeledIdx = i;
                            break;
                        }}
                    }}

                    if (nextUnlabeledIdx === -1) {{
                        // 如果后面没有未标注的，从头找
                        for (let i = 0; i < currentImageIdx; i++) {{
                            if (!imageList[i].labeled) {{
                                nextUnlabeledIdx = i;
                                break;
                            }}
                        }}
                    }}

                    if (nextUnlabeledIdx !== -1) {{
                        loadImageAtIndex(nextUnlabeledIdx);
                    }} else {{
                        alert('恭喜！所有图片都已标注完成！');
                        // 重新加载当前图片以显示已标注状态
                        loadImageAtIndex(currentImageIdx);
                    }}
                }} else {{
                    location.reload();
                }}
            }} else {{
                alert('保存失败');
            }}
        }}

        async function startTraining() {{
            if (currentClasses.length === 0) {{
                alert('请先设置类别');
                return;
            }}

            // 收集所有参数
            const params = {{
                model: document.getElementById('modelSize').value,
                epochs: parseInt(document.getElementById('epochs').value),
                batch: parseInt(document.getElementById('batchSize').value),
                imgsz: parseInt(document.getElementById('imgSize').value),
                lr: parseFloat(document.getElementById('lr').value),
                momentum: parseFloat(document.getElementById('momentum').value),
                weight_decay: parseFloat(document.getElementById('weightDecay').value),
                warmup_epochs: parseInt(document.getElementById('warmupEpochs').value),
                hsv_h: parseFloat(document.getElementById('hsvH').value),
                hsv_s: parseFloat(document.getElementById('hsvS').value),
                hsv_v: parseFloat(document.getElementById('hsvV').value),
                degrees: parseInt(document.getElementById('degrees').value),
                fliplr: parseFloat(document.getElementById('flipLr').value),
                mosaic: parseFloat(document.getElementById('mosaic').value),
                patience: parseInt(document.getElementById('patience').value),
                conf: parseFloat(document.getElementById('confThresh').value),
                iou: parseFloat(document.getElementById('iouThresh').value),
                workers: parseInt(document.getElementById('workers').value),
                name: document.getElementById('projectName').value || 'custom_model'
            }};

            document.getElementById('trainingOutput').style.display = 'block';
            document.getElementById('trainingOutput').textContent = '准备开始训练...\\n参数: ' + JSON.stringify(params, null, 2);

            const response = await fetch('/api/train', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(params)
            }});

            if (response.ok) {{
                const data = await response.json();
                document.getElementById('trainingOutput').textContent += '\\n\\n' + data.message;
            }} else {{
                document.getElementById('trainingOutput').textContent += '\\n\\n训练失败！';
            }}
        }}

        async function testModel() {{
            const modelPath = document.getElementById('testModelSelect').value;
            const file = document.getElementById('testImage').files[0];

            if (!modelPath) {{
                alert('请选择测试模型');
                return;
            }}
            if (!file) {{
                alert('请上传测试图片');
                return;
            }}

            const formData = new FormData();
            formData.append('image', file);
            formData.append('model_path', modelPath);
            formData.append('conf', document.getElementById('testConf').value);
            formData.append('iou', document.getElementById('testIou').value);

            document.getElementById('testResult').innerHTML = '<p>检测中...</p>';

            const response = await fetch('/api/test', {{
                method: 'POST',
                body: formData
            }});

            if (response.ok) {{
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                document.getElementById('testResult').innerHTML =
                    '<img src="' + url + '" style="max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">';

                // 显示检测信息
                const info = await response.headers.get('X-Detection-Info');
                if (info) {{
                    document.getElementById('testInfo').innerHTML =
                        '<div class="success-box"><strong>检测完成！</strong><br>' + decodeURIComponent(info) + '</div>';
                }}
            }} else {{
                document.getElementById('testResult').innerHTML = '<p style="color: red;">检测失败</p>';
            }}
        }}
    </script>
</body>
</html>
    '''
    return html

@app.route('/api/classes', methods=['POST'])
def add_class():
    """添加类别"""
    data = request.json
    classes = load_classes()
    classes.append(data['name'])
    save_classes(classes)
    return jsonify({'success': True, 'classes': classes})

@app.route('/api/save-annotation', methods=['POST'])
def save_annotation():
    """保存标注"""
    try:
        file = request.files['image']
        dataset_type = request.form['dataset_type']
        annotations = json.loads(request.form['annotations'])
        img_width = float(request.form['image_width'])
        img_height = float(request.form['image_height'])

        filename = secure_filename(file.filename)
        img_path = DATASET_DIR / 'images' / dataset_type / filename
        file.save(str(img_path))

        label_filename = Path(filename).stem + '.txt'
        label_path = DATASET_DIR / 'labels' / dataset_type / label_filename

        with open(label_path, 'w') as f:
            for ann in annotations:
                x_center = (ann['x'] + ann['width'] / 2) / img_width
                y_center = (ann['y'] + ann['height'] / 2) / img_height
                width = ann['width'] / img_width
                height = ann['height'] / img_height
                f.write(f"{ann['classId']} {x_center} {y_center} {width} {height}\n")

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    """开始训练"""
    try:
        params = request.json
        classes = load_classes()

        data_yaml = {
            'path': str(DATASET_DIR.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': len(classes),
            'names': classes
        }

        data_yaml_path = DATASET_DIR / 'data.yaml'
        with open(data_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data_yaml, f, allow_unicode=True)

        model = YOLO(params['model'])

        # 使用所有参数进行训练
        results = model.train(
            data=str(data_yaml_path),
            epochs=params['epochs'],
            batch=params['batch'],
            imgsz=params['imgsz'],
            lr0=params['lr'],
            momentum=params['momentum'],
            weight_decay=params['weight_decay'],
            warmup_epochs=params['warmup_epochs'],
            hsv_h=params['hsv_h'],
            hsv_s=params['hsv_s'],
            hsv_v=params['hsv_v'],
            degrees=params['degrees'],
            fliplr=params['fliplr'],
            mosaic=params['mosaic'],
            patience=params['patience'],
            conf=params['conf'],
            iou=params['iou'],
            workers=params['workers'],
            name=params['name'],
            save=True,
            device='cpu',
            project=str(MODELS_DIR)
        )

        model_path = MODELS_DIR / 'runs' / 'detect' / params['name'] / 'weights' / 'best.pt'

        return jsonify({
            'success': True,
            'message': f'训练完成！\n模型保存在: {model_path}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test_model():
    """测试模型"""
    try:
        file = request.files['image']
        model_path = request.form.get('model_path', 'yolov8n.pt')
        conf = float(request.form.get('conf', 0.25))
        iou = float(request.form.get('iou', 0.45))

        image = Image.open(file.stream).convert('RGB')

        model = YOLO(model_path)
        results = model.predict(image, conf=conf, iou=iou, verbose=False)[0]

        # 统计检测结果
        num_detections = len(results.boxes)
        detection_info = f'检测到 {num_detections} 个物体'

        annotated_img = results.plot()
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_bytes = io.BytesIO(buffer.tobytes())

        response = send_file(img_bytes, mimetype='image/jpeg')
        response.headers['X-Detection-Info'] = detection_info
        return response
    except Exception as e:
        return str(e), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """列出所有可用模型"""
    return jsonify({'models': get_available_models()})

@app.route('/api/dataset-path', methods=['GET'])
def get_dataset_path():
    """获取当前数据集路径"""
    return jsonify({'dataset_path': str(DATASET_DIR.absolute())})

@app.route('/api/dataset-path', methods=['POST'])
def set_dataset_path():
    """设置数据集路径"""
    global DATASET_DIR
    try:
        data = request.json
        new_path = Path(data['path'])

        # 确保目录结构
        DATASET_DIR = ensure_dataset_structure(new_path)
        save_dataset_config(DATASET_DIR)

        return jsonify({
            'success': True,
            'dataset_path': str(DATASET_DIR.absolute())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/folder-images', methods=['POST'])
def load_folder_images():
    """从文件夹加载图片列表"""
    try:
        data = request.json
        folder_path = Path(data['folder_path'])
        dataset_type = data.get('dataset_type', 'train')

        if not folder_path.exists() or not folder_path.is_dir():
            return jsonify({'success': False, 'error': '文件夹不存在'}), 400

        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}
        images = []

        for file in folder_path.iterdir():
            if file.suffix.lower() in image_extensions:
                images.append({
                    'path': str(file.absolute()),
                    'name': file.name,
                    'labeled': (DATASET_DIR / 'labels' / dataset_type / f'{file.stem}.txt').exists()
                })

        return jsonify({
            'success': True,
            'images': sorted(images, key=lambda x: x['name']),
            'total': len(images)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load-image', methods=['POST'])
def load_image_file():
    """从本地文件系统读取图片"""
    try:
        data = request.json
        image_path = Path(data['path'])

        if not image_path.exists() or not image_path.is_file():
            return jsonify({'success': False, 'error': '图片文件不存在'}), 400

        return send_file(str(image_path), mimetype='image/jpeg')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🎯 YOLOv8 训练系统 V2 - 专业版")
    print("=" * 70)
    print("\n✓ 服务器启动成功")
    print("\n浏览器访问: http://localhost:7865")
    print("\n新功能:")
    print("  ✅ 测试时可选择不同模型")
    print("  ✅ 20+ 训练参数可调节")
    print("  ✅ 完整的数据增强选项")
    print("  ✅ 优化器参数自定义")
    print("\n数据集位置:")
    print(f"  {DATASET_DIR.absolute()}")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 70 + "\n")

    app.run(host='0.0.0.0', port=7865, debug=False)
