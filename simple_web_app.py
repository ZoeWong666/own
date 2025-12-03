"""
超简洁的目标检测Web界面 - 使用 Flask
上传图片 → 检测 → 显示结果
"""
from flask import Flask, render_template, request, send_file
from ultralytics import YOLO
from PIL import Image
import io
import base64
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 限制

# 加载模型
model = None

def load_model_once():
    global model
    if model is None:
        print("正在加载检测模型...")
        model = YOLO('yolov8n.pt')
        print("✓ 模型加载完成")
    return model

@app.route('/')
def index():
    """主页"""
    html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 目标检测</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.2em;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 60px 20px;
            text-align: center;
            background: #f8f9ff;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 30px;
        }

        .upload-area:hover {
            background: #f0f2ff;
            border-color: #5568d3;
        }

        .upload-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }

        input[type="file"] {
            display: none;
        }

        .upload-text {
            font-size: 1.2em;
            color: #667eea;
            margin-bottom: 10px;
        }

        .upload-hint {
            color: #999;
            font-size: 0.9em;
        }

        .detect-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.3em;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 30px;
            display: none;
        }

        .detect-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
        }

        .detect-btn:active {
            transform: translateY(0);
        }

        .preview-container {
            display: none;
            margin-bottom: 30px;
        }

        .preview-image {
            width: 100%;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .result-container {
            display: none;
        }

        .result-image {
            width: 100%;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 3px solid #4CAF50;
        }

        .loading {
            text-align: center;
            display: none;
            margin: 30px 0;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .footer {
            text-align: center;
            color: #999;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }

        .success-badge {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AI 目标检测</h1>
        <p class="subtitle">上传图片，自动识别并标注所有物体</p>

        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📁</div>
                <div class="upload-text">点击上传图片</div>
                <div class="upload-hint">支持 JPG、PNG、BMP 格式</div>
                <input type="file" id="fileInput" name="image" accept="image/*" onchange="handleFileSelect(event)">
            </div>

            <div class="preview-container" id="previewContainer">
                <h3>预览图片：</h3>
                <img id="previewImage" class="preview-image">
            </div>

            <button type="submit" class="detect-btn" id="detectBtn">
                🔍 开始检测
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>正在检测中，请稍候...</p>
        </div>

        <div class="result-container" id="resultContainer">
            <span class="success-badge">✓ 检测完成</span>
            <h3>检测结果：</h3>
            <img id="resultImage" class="result-image">
        </div>

        <div class="footer">
            <p>💻 基于 YOLOv8 深度学习模型</p>
            <p>支持 80 种常见物体识别 | 本地运行 | 保护隐私</p>
        </div>
    </div>

    <script>
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('previewImage').src = e.target.result;
                    document.getElementById('previewContainer').style.display = 'block';
                    document.getElementById('detectBtn').style.display = 'block';
                    document.getElementById('resultContainer').style.display = 'none';
                }
                reader.readAsDataURL(file);
            }
        }

        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files[0]) {
                alert('请先选择图片');
                return;
            }

            // 显示加载动画
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultContainer').style.display = 'none';
            document.getElementById('detectBtn').disabled = true;

            // 上传并检测
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);

                    document.getElementById('resultImage').src = imageUrl;
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('resultContainer').style.display = 'block';
                    document.getElementById('detectBtn').disabled = false;

                    // 滚动到结果区域
                    document.getElementById('resultContainer').scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert('检测失败，请重试');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('detectBtn').disabled = false;
                }
            } catch (error) {
                alert('发生错误: ' + error.message);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('detectBtn').disabled = false;
            }
        });
    </script>
</body>
</html>
    '''
    return html

@app.route('/detect', methods=['POST'])
def detect():
    """检测图片"""
    if 'image' not in request.files:
        return '没有上传图片', 400

    file = request.files['image']
    if file.filename == '':
        return '没有选择文件', 400

    try:
        # 读取图片
        image = Image.open(file.stream).convert('RGB')

        # 加载模型
        model = load_model_once()

        # 检测
        results = model.predict(image, conf=0.25, verbose=False)[0]

        # 绘制结果
        import cv2
        annotated_img = results.plot()

        # 转换为 bytes
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_bytes = io.BytesIO(buffer.tobytes())

        return send_file(img_bytes, mimetype='image/jpeg')

    except Exception as e:
        print(f"错误: {e}")
        return f'检测失败: {str(e)}', 500

if __name__ == '__main__':
    # 预加载模型
    load_model_once()

    print("\n" + "="*70)
    print("🎯 AI 目标检测系统")
    print("="*70)
    print("\n✓ 服务器启动成功")
    print("\n浏览器访问: http://localhost:7863")
    print("\n按 Ctrl+C 停止服务")
    print("="*70 + "\n")

    app.run(host='0.0.0.0', port=7863, debug=False)
