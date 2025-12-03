# 🔌 API 使用指南

## REST API 接口文档

本项目提供完整的REST API，方便集成到其他应用中。

## 启动API服务

```bash
python detection_api.py
```

服务启动后：
- API地址: http://localhost:8000
- 交互式文档: http://localhost:8000/docs
- OpenAPI规范: http://localhost:8000/openapi.json

## API端点

### 1. 检测单张图片

**端点**: `POST /detect`

**请求**:
```python
import requests

with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect',
        files={'image': f},
        data={
            'conf_threshold': 0.25,  # 可选，默认0.25
            'iou_threshold': 0.45    # 可选，默认0.45
        }
    )

result = response.json()
```

**响应**:
```json
{
  "success": true,
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.92,
      "bbox": {
        "x1": 100,
        "y1": 50,
        "x2": 300,
        "y2": 400
      }
    },
    {
      "class_id": 2,
      "class_name": "car",
      "confidence": 0.85,
      "bbox": {
        "x1": 350,
        "y1": 200,
        "x2": 600,
        "y2": 450
      }
    }
  ],
  "count": 2,
  "image_size": {
    "width": 800,
    "height": 600
  }
}
```

### 2. 批量检测

**端点**: `POST /detect_batch`

**请求**:
```python
import requests

files = [
    ('images', open('img1.jpg', 'rb')),
    ('images', open('img2.jpg', 'rb')),
    ('images', open('img3.jpg', 'rb'))
]

response = requests.post(
    'http://localhost:8000/detect_batch',
    files=files,
    data={'conf_threshold': 0.3}
)

results = response.json()
```

**响应**:
```json
{
  "success": true,
  "results": [
    {
      "filename": "img1.jpg",
      "detections": [...],
      "count": 3
    },
    {
      "filename": "img2.jpg",
      "detections": [...],
      "count": 1
    },
    {
      "filename": "img3.jpg",
      "detections": [...],
      "count": 5
    }
  ],
  "total_images": 3,
  "total_detections": 9
}
```

### 3. 获取标注图片

**端点**: `POST /detect_annotated`

返回带标注框的图片（而不是JSON）。

**请求**:
```python
import requests
from PIL import Image
import io

with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect_annotated',
        files={'image': f}
    )

# 保存结果图片
if response.status_code == 200:
    img = Image.open(io.BytesIO(response.content))
    img.save('result.jpg')
```

### 4. 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

## 完整示例

### Python

```python
import requests
from pathlib import Path

class YOLOClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url

    def detect(self, image_path, conf=0.25, iou=0.45):
        """检测单张图片"""
        with open(image_path, 'rb') as f:
            response = requests.post(
                f'{self.base_url}/detect',
                files={'image': f},
                data={
                    'conf_threshold': conf,
                    'iou_threshold': iou
                }
            )
        return response.json()

    def detect_batch(self, image_paths, conf=0.25):
        """批量检测"""
        files = [('images', open(p, 'rb')) for p in image_paths]
        response = requests.post(
            f'{self.base_url}/detect_batch',
            files=files,
            data={'conf_threshold': conf}
        )
        # 关闭文件
        for _, f in files:
            f.close()
        return response.json()

    def get_annotated_image(self, image_path, output_path):
        """获取标注图片"""
        with open(image_path, 'rb') as f:
            response = requests.post(
                f'{self.base_url}/detect_annotated',
                files={'image': f}
            )

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False

# 使用示例
client = YOLOClient()

# 检测单张图片
result = client.detect('test.jpg', conf=0.3)
print(f"检测到 {result['count']} 个物体")
for det in result['detections']:
    print(f"- {det['class_name']}: {det['confidence']:.2%}")

# 批量检测
results = client.detect_batch(['img1.jpg', 'img2.jpg', 'img3.jpg'])
print(f"总共检测: {results['total_detections']} 个物体")

# 获取标注图片
client.get_annotated_image('test.jpg', 'result.jpg')
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class YOLOClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async detect(imagePath, conf = 0.25, iou = 0.45) {
        const form = new FormData();
        form.append('image', fs.createReadStream(imagePath));
        form.append('conf_threshold', conf);
        form.append('iou_threshold', iou);

        const response = await axios.post(
            `${this.baseUrl}/detect`,
            form,
            { headers: form.getHeaders() }
        );

        return response.data;
    }

    async detectAnnotated(imagePath, outputPath) {
        const form = new FormData();
        form.append('image', fs.createReadStream(imagePath));

        const response = await axios.post(
            `${this.baseUrl}/detect_annotated`,
            form,
            {
                headers: form.getHeaders(),
                responseType: 'arraybuffer'
            }
        );

        fs.writeFileSync(outputPath, response.data);
    }
}

// 使用
const client = new YOLOClient();

client.detect('test.jpg', 0.3)
    .then(result => {
        console.log(`检测到 ${result.count} 个物体`);
        result.detections.forEach(det => {
            console.log(`- ${det.class_name}: ${(det.confidence * 100).toFixed(2)}%`);
        });
    });
```

### cURL

```bash
# 检测图片
curl -X POST http://localhost:8000/detect \
  -F "image=@test.jpg" \
  -F "conf_threshold=0.25"

# 获取标注图片
curl -X POST http://localhost:8000/detect_annotated \
  -F "image=@test.jpg" \
  -o result.jpg

# 健康检查
curl http://localhost:8000/health
```

## 参数说明

### conf_threshold (置信度阈值)
- 类型: float
- 范围: 0.0 - 1.0
- 默认: 0.25
- 说明: 只返回置信度高于此值的检测结果
- 建议:
  - 0.15-0.25: 检测更多物体（可能有误检）
  - 0.25-0.5: 平衡
  - 0.5-0.9: 只检测高置信度物体（可能漏检）

### iou_threshold (IoU阈值)
- 类型: float
- 范围: 0.0 - 1.0
- 默认: 0.45
- 说明: NMS（非极大值抑制）的IoU阈值
- 建议:
  - 0.3-0.4: 更激进的去重
  - 0.45-0.5: 标准设置
  - 0.6-0.7: 保留更多重叠框

## 错误处理

### 常见错误码

- **400 Bad Request**: 请求参数错误
  ```json
  {
    "error": "No image provided"
  }
  ```

- **413 Payload Too Large**: 图片太大
  ```json
  {
    "error": "File size exceeds limit"
  }
  ```

- **500 Internal Server Error**: 服务器错误
  ```json
  {
    "error": "Model inference failed"
  }
  ```

### 错误处理示例

```python
try:
    result = client.detect('test.jpg')
    if result['success']:
        print(f"检测成功: {result['count']} 个物体")
    else:
        print(f"检测失败: {result.get('error', 'Unknown error')}")
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
```

## 性能优化

### 1. 批量检测
批量检测比单独检测更高效：
```python
# ❌ 慢
for img in images:
    client.detect(img)

# ✅ 快
client.detect_batch(images)
```

### 2. 连接复用
使用Session复用连接：
```python
import requests

session = requests.Session()
response = session.post('http://localhost:8000/detect', ...)
```

### 3. 异步请求
使用异步库提高并发：
```python
import asyncio
import aiohttp

async def detect_async(session, image_path):
    async with session.post(
        'http://localhost:8000/detect',
        data={'image': open(image_path, 'rb')}
    ) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [detect_async(session, img) for img in images]
        results = await asyncio.gather(*tasks)
```

## 部署建议

### 生产环境部署

不要使用Flask开发服务器，使用Gunicorn：

```bash
# 安装
pip install gunicorn

# 启动（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:8000 detection_api:app
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "detection_api:app"]
```

```bash
docker build -t yolo-api .
docker run -p 8000:8000 yolo-api
```

## 安全建议

1. **添加认证**:
```python
from flask import request

@app.before_request
def check_auth():
    token = request.headers.get('Authorization')
    if token != 'your-secret-token':
        return jsonify({'error': 'Unauthorized'}), 401
```

2. **限流**:
```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])

@app.route('/detect')
@limiter.limit("10 per minute")
def detect():
    ...
```

3. **HTTPS**: 生产环境使用HTTPS

## 监控

添加日志和监控：
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/detect', methods=['POST'])
def detect():
    logger.info(f"Received detection request from {request.remote_addr}")
    # ...
```

## 更多资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [YOLOv8 Python API](https://docs.ultralytics.com/usage/python/)
- [项目GitHub](https://github.com/your-repo)

**需要帮助？查看 [README.md](README.md)**
