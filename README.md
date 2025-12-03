# 🎯 YOLOv8 训练系统

一站式 YOLOv8 目标检测训练平台，包含数据标注、模型训练、效果测试全流程。

## ✨ 功能特点

### 🎨 可视化界面
- 友好的Web界面，无需编程
- 分步骤引导（设置类别 → 标注数据 → 训练模型 → 测试效果）
- 实时统计数据展示

### 🖼️ 集成标注工具
- 内置图片标注功能（类似LabelImg）
- 鼠标拖动框选物体
- 支持多物体标注
- 自动生成YOLO格式标注文件

### ⚙️ 20+ 训练参数
- 基础参数：模型大小、轮数、批次、图片尺寸
- 优化器：学习率、动量、权重衰减、预热轮数
- 数据增强：色调、饱和度、亮度、旋转、翻转、马赛克
- 其他：早停、置信度阈值、IoU阈值、工作线程数

### 🧪 灵活测试
- 下拉框选择测试模型
- 支持预训练模型和自定义模型
- 可调节置信度和IoU阈值
- 实时显示检测结果

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 建议使用虚拟环境

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动系统

```bash
# 方式1: 启动专业版（推荐）
python yolo_training_system_v2.py

# 方式2: 启动基础版
python yolo_training_system.py

# 方式3: 简洁检测界面（不含训练功能）
python simple_web_app.py
```

### 4. 访问界面

打开浏览器访问：
- **专业版**: http://localhost:7865
- **基础版**: http://localhost:7864
- **简洁版**: http://localhost:7863

## 📖 使用流程

### 步骤 1: 设置类别

1. 定义你要检测的物体类别
2. 例如：person, car, dog, cat, chair
3. 支持中文和英文类别名称

### 步骤 2: 标注数据

1. 上传图片（训练集或验证集）
2. 在图片上拖动鼠标框选物体
3. 选择物体类别ID
4. 保存标注

**数据建议**:
- 每个类别至少100-200张图片
- 训练集:验证集 = 8:2
- 图片质量要好，标注要准确

### 步骤 3: 训练模型

#### 基础参数
- **模型大小**: Nano(最快) → XLarge(最精确)
- **训练轮数**: 100-300轮（数据少时用更多轮数）
- **批次大小**: 16-32（显存不足时减小）
- **图片大小**: 640（标准）或 1280（高精度）

#### 高级参数（专业版）
- 学习率、动量、权重衰减
- 色调、饱和度、亮度调整
- 旋转、翻转、马赛克增强
- 早停、置信度阈值等

#### 开始训练
点击"开始训练"按钮，等待训练完成。

**训练时间参考**:
- CPU: 100轮约 4-8小时
- GPU: 100轮约 1-2小时

### 步骤 4: 测试模型

1. 从下拉框选择训练好的模型
2. 上传测试图片
3. 调整置信度阈值（可选）
4. 查看检测结果

## 📁 目录结构

```
yolo-training-system/
├── yolo_training_system_v2.py   # 专业版训练系统（推荐）
├── yolo_training_system.py      # 基础版训练系统
├── simple_web_app.py             # 简洁检测界面
├── detection_api.py              # REST API接口
├── requirements.txt              # Python依赖
├── README.md                     # 本文件
├── USAGE_GUIDE.md                # 详细使用指南
├── API_GUIDE.md                  # API文档
└── yolo_workspace/               # 工作目录（自动创建）
    ├── dataset/                  # 数据集
    │   ├── images/
    │   │   ├── train/
    │   │   └── val/
    │   ├── labels/
    │   │   ├── train/
    │   │   └── val/
    │   └── data.yaml             # 数据配置
    ├── models/                   # 训练好的模型
    │   └── runs/detect/
    │       └── custom_model/
    │           └── weights/
    │               └── best.pt
    └── classes.json              # 类别配置
```

## 💻 API 使用

### 启动 API 服务

```bash
python detection_api.py
```

访问 API 文档: http://localhost:8000/docs

### 检测图片

```python
import requests

with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect',
        files={'image': f},
        data={'conf_threshold': 0.25}
    )

result = response.json()
print(result['detections'])
```

详细 API 文档见 [API_GUIDE.md](API_GUIDE.md)

## 🎓 常见问题

### Q1: 数据量不够怎么办？
- 使用数据增强（系统自动）
- 使用预训练模型微调
- 收集更多数据（推荐）

### Q2: 训练速度慢？
- 使用更小的模型（Nano）
- 减小batch_size
- 使用GPU训练（需要CUDA）

### Q3: 精度不够？
- 增加训练数据
- 使用更大的模型（Large/XLarge）
- 增加训练轮数
- 检查标注质量

### Q4: 显存不足？
- 减小batch_size（例如从16减到8）
- 减小图片尺寸（例如从640减到320）
- 使用更小的模型

### Q5: 如何使用GPU训练？
在代码中修改：
```python
device='cuda'  # 默认是 'cpu'
```

## 🔧 高级用法

### 命令行训练

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.train(
    data='yolo_workspace/dataset/data.yaml',
    epochs=100,
    batch=16,
    imgsz=640,
    device='cpu'  # 或 'cuda'
)
```

### Python 推理

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('yolo_workspace/models/runs/detect/custom_model/weights/best.pt')

# 检测
results = model.predict('test.jpg', conf=0.25)

# 显示结果
results[0].show()

# 或保存结果
results[0].save('result.jpg')
```

## 📦 导出模型

### 导出为 ONNX（通用格式）

```python
model = YOLO('best.pt')
model.export(format='onnx')
```

### 导出为移动端格式

```python
# iOS
model.export(format='coreml')

# Android
model.export(format='tflite')
```

## 🌟 特色功能

### 1. 实时统计
- 顶部卡片显示数据集统计
- 自动更新类别数量、图片数量、标注进度

### 2. 路径提示
- 每个步骤都显示文件保存位置
- 方便查找数据集和模型

### 3. 参数说明
- 每个参数都有详细说明
- 推荐值提示
- 帮助文本引导

### 4. 多模型管理
- 自动扫描所有可用模型
- 支持预训练模型和自定义模型
- 下拉框方便切换

## 📝 依赖说明

核心依赖：
- **ultralytics**: YOLOv8官方库
- **flask**: Web框架
- **opencv-python**: 图像处理
- **pillow**: 图像库
- **pyyaml**: 配置文件
- **torch**: 深度学习框架（自动安装）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 技术支持

遇到问题？查看：
- [使用指南](USAGE_GUIDE.md)
- [API文档](API_GUIDE.md)
- [YOLOv8官方文档](https://docs.ultralytics.com/)

---

**祝你训练愉快！🎯🚀**
