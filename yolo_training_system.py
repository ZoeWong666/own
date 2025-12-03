"""
YOLOv8 完整训练系统 - 包含标注、训练、测试功能
使用Flask创建友好的Web界面
"""
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
import shutil
from pathlib import Path
import yaml
from PIL import Image
import io
import base64
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB限制

# 工作目录
WORKSPACE = Path('yolo_workspace')
WORKSPACE.mkdir(exist_ok=True)

# 数据集目录
DATASET_DIR = WORKSPACE / 'dataset'
DATASET_DIR.mkdir(exist_ok=True)
(DATASET_DIR / 'images' / 'train').mkdir(parents=True, exist_ok=True)
(DATASET_DIR / 'images' / 'val').mkdir(parents=True, exist_ok=True)
(DATASET_DIR / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
(DATASET_DIR / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

# 临时上传目录
UPLOAD_DIR = WORKSPACE / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

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

@app.route('/')
def index():
    """主页 - 工作台"""
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

    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YOLOv8 训练系统</title>
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

        label {{
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
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

        .canvas-container {{
            position: relative;
            margin: 20px 0;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 YOLOv8 训练系统</h1>
        <p class="subtitle">数据标注 → 模型训练 → 效果测试 一站式解决方案</p>

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
                <div class="section-title">📝 定义检测类别</div>

                <div class="info-box">
                    <strong>💡 提示:</strong> 先定义你要检测的物体类别，例如：人、车、狗、猫、椅子
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
                        <li>上传图片到训练集或验证集</li>
                        <li>在图片上拖动鼠标框选物体</li>
                        <li>选择物体类别并保存</li>
                        <li>重复以上步骤标注所有图片</li>
                    </ol>
                </div>

                <div class="form-group">
                    <label>选择数据集类型</label>
                    <select id="datasetType">
                        <option value="train">训练集 (80%图片)</option>
                        <option value="val">验证集 (20%图片)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>上传图片</label>
                    <input type="file" id="imageUpload" accept="image/*" onchange="loadImage()" multiple>
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
                <div class="section-title">🚀 模型训练</div>

                <div class="warning-box">
                    <strong>⚠️ 训练前检查:</strong>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>已定义类别: {len(classes)} 个</li>
                        <li>训练集图片: {stats['train_images']} 张（已标注: {stats['train_labeled']}）</li>
                        <li>验证集图片: {stats['val_images']} 张（已标注: {stats['val_labeled']}）</li>
                        <li>建议每个类别至少100张标注图片</li>
                    </ul>
                </div>

                <div class="form-group">
                    <label>选择模型大小</label>
                    <select id="modelSize">
                        <option value="yolov8n.pt">Nano (最快，适合实时检测)</option>
                        <option value="yolov8s.pt">Small (平衡速度和精度)</option>
                        <option value="yolov8m.pt">Medium (更高精度)</option>
                        <option value="yolov8l.pt">Large (最高精度，较慢)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>训练轮数 (Epochs)</label>
                    <input type="number" id="epochs" value="100" min="1">
                </div>

                <div class="form-group">
                    <label>批次大小 (Batch Size)</label>
                    <input type="number" id="batchSize" value="16" min="1">
                </div>

                <button class="btn" onclick="startTraining()">🎯 开始训练</button>

                <div id="trainingOutput" class="training-output" style="display:none;">
                    训练日志将显示在这里...
                </div>

                <div class="path-box">
                    <strong>💾 模型保存位置:</strong><br>
                    {MODELS_DIR.absolute()}/runs/detect/custom_model/weights/best.pt
                </div>
            </div>
        </div>

        <!-- 标签页4: 测试模型 -->
        <div id="test-tab" class="tab-content">
            <div class="section">
                <div class="section-title">🧪 测试模型</div>

                <div class="info-box">
                    <strong>💡 提示:</strong> 上传图片测试训练好的模型效果
                </div>

                <div class="form-group">
                    <label>上传测试图片</label>
                    <input type="file" id="testImage" accept="image/*">
                </div>

                <button class="btn" onclick="testModel()">🔍 开始检测</button>

                <div id="testResult" style="margin-top: 20px;"></div>
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

        function switchTab(tabName) {{
            // 隐藏所有标签页
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

            // 显示选中的标签页
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

        function loadImage() {{
            const file = document.getElementById('imageUpload').files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {{
                const img = new Image();
                img.onload = function() {{
                    canvas = document.getElementById('annotationCanvas');
                    ctx = canvas.getContext('2d');

                    // 调整canvas大小
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

                    // 设置鼠标事件
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

            // 重绘图像和现有标注
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(currentImage, 0, 0, canvas.width, canvas.height);

            // 绘制当前框
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

            // 弹窗选择类别
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

                // 重绘所有标注
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

            const file = document.getElementById('imageUpload').files[0];
            const datasetType = document.getElementById('datasetType').value;

            const formData = new FormData();
            formData.append('image', file);
            formData.append('dataset_type', datasetType);
            formData.append('annotations', JSON.stringify(annotations));
            formData.append('image_width', canvas.width);
            formData.append('image_height', canvas.height);

            const response = await fetch('/api/save-annotation', {{
                method: 'POST',
                body: formData
            }});

            if (response.ok) {{
                alert('标注保存成功！');
                annotations = [];
                location.reload();  // 刷新统计数据
            }} else {{
                alert('保存失败');
            }}
        }}

        async function startTraining() {{
            if (currentClasses.length === 0) {{
                alert('请先设置类别');
                return;
            }}

            const modelSize = document.getElementById('modelSize').value;
            const epochs = document.getElementById('epochs').value;
            const batchSize = document.getElementById('batchSize').value;

            document.getElementById('trainingOutput').style.display = 'block';
            document.getElementById('trainingOutput').textContent = '准备开始训练...\\n';

            const response = await fetch('/api/train', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    model: modelSize,
                    epochs: parseInt(epochs),
                    batch: parseInt(batchSize)
                }})
            }});

            if (response.ok) {{
                const data = await response.json();
                document.getElementById('trainingOutput').textContent += data.message;
            }}
        }}

        async function testModel() {{
            const file = document.getElementById('testImage').files[0];
            if (!file) {{
                alert('请先上传图片');
                return;
            }}

            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/api/test', {{
                method: 'POST',
                body: formData
            }});

            if (response.ok) {{
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                document.getElementById('testResult').innerHTML =
                    '<img src="' + url + '" style="max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">';
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
        dataset_type = request.form['dataset_type']  # train or val
        annotations = json.loads(request.form['annotations'])
        img_width = float(request.form['image_width'])
        img_height = float(request.form['image_height'])

        # 保存图片
        filename = secure_filename(file.filename)
        img_path = DATASET_DIR / 'images' / dataset_type / filename
        file.save(str(img_path))

        # 保存标注文件 (YOLO格式)
        label_filename = Path(filename).stem + '.txt'
        label_path = DATASET_DIR / 'labels' / dataset_type / label_filename

        with open(label_path, 'w') as f:
            for ann in annotations:
                # 转换为YOLO格式 (归一化坐标)
                x_center = (ann['x'] + ann['width'] / 2) / img_width
                y_center = (ann['y'] + ann['height'] / 2) / img_height
                width = ann['width'] / img_width
                height = ann['height'] / img_height

                f.write(f"{ann['classId']} {x_center} {y_center} {width} {height}\\n")

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    """开始训练"""
    try:
        data = request.json
        classes = load_classes()

        # 创建data.yaml
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

        # 开始训练
        model = YOLO(data['model'])
        results = model.train(
            data=str(data_yaml_path),
            epochs=data['epochs'],
            batch=data['batch'],
            imgsz=640,
            name='custom_model',
            patience=50,
            save=True,
            device='cpu',
            project=str(MODELS_DIR)
        )

        return jsonify({
            'success': True,
            'message': f'训练完成！\\n模型保存在: {MODELS_DIR}/runs/detect/custom_model/weights/best.pt'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test_model():
    """测试模型"""
    try:
        file = request.files['image']
        image = Image.open(file.stream).convert('RGB')

        # 查找最新的模型
        model_path = MODELS_DIR / 'runs' / 'detect' / 'custom_model' / 'weights' / 'best.pt'

        if not model_path.exists():
            # 使用预训练模型
            model_path = 'yolov8n.pt'

        model = YOLO(str(model_path))
        results = model.predict(image, conf=0.25, verbose=False)[0]

        # 绘制结果
        annotated_img = results.plot()

        # 转换为bytes
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_bytes = io.BytesIO(buffer.tobytes())

        return send_file(img_bytes, mimetype='image/jpeg')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print("\\n" + "=" * 70)
    print("🎯 YOLOv8 训练系统")
    print("=" * 70)
    print("\\n✓ 服务器启动成功")
    print("\\n浏览器访问: http://localhost:7864")
    print("\\n功能:")
    print("  1. 设置类别 - 定义要检测的物体类别")
    print("  2. 标注数据 - 在图片上框选并标注物体")
    print("  3. 开始训练 - 训练自定义检测模型")
    print("  4. 测试模型 - 测试训练好的模型效果")
    print("\\n数据集位置:")
    print(f"  {DATASET_DIR.absolute()}")
    print("\\n按 Ctrl+C 停止服务")
    print("=" * 70 + "\\n")

    app.run(host='0.0.0.0', port=7864, debug=False)
