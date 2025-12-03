# 📋 项目信息

## 项目概述

**项目名称**: YOLOv8训练系统
**项目位置**: `/Users/wangzuoming/Desktop/yolo-training-system`
**版本**: 1.0.0
**创建日期**: 2025-12-03

## 项目结构

```
yolo-training-system/
├── 📄 README.md                      # 项目主文档
├── 📄 QUICK_START.md                 # 快速开始指南
├── 📄 API_GUIDE.md                   # API使用文档
├── 📄 requirements.txt               # Python依赖列表
├── 📄 .gitignore                     # Git忽略规则
├── 🚀 start.sh                       # 快速启动脚本
│
├── 🎯 核心功能文件:
│   ├── yolo_training_system_v2.py   # 专业版训练系统 ⭐推荐
│   ├── yolo_training_system.py      # 基础版训练系统
│   ├── simple_web_app.py            # 简洁检测界面
│   └── detection_api.py             # REST API接口
│
└── 📁 examples/                      # 使用示例
    └── python_client.py             # Python客户端示例
```

## 功能模块

### 1. yolo_training_system_v2.py（专业版）⭐
**端口**: 7865
**功能**:
- ✅ 设置类别（支持中英文）
- ✅ 图片标注（内置LabelImg功能）
- ✅ 模型训练（20+可调参数）
- ✅ 模型测试（下拉框选择模型）

**特色**:
- 完整的参数面板（基础、优化器、数据增强）
- 支持选择不同模型进行测试
- 实时数据统计展示
- 路径提示和帮助文档

### 2. yolo_training_system.py（基础版）
**端口**: 7864
**功能**: 与专业版类似，但参数较少，界面更简洁

### 3. simple_web_app.py（简洁检测）
**端口**: 7863
**功能**:
- 上传图片
- 一键检测
- 查看结果
- 无训练功能，只做检测

### 4. detection_api.py（REST API）
**端口**: 8000
**功能**:
- `/detect` - 单图检测
- `/detect_batch` - 批量检测
- `/detect_annotated` - 返回标注图片
- `/health` - 健康检查

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 编程语言 |
| PyTorch | 2.0+ | 深度学习框架 |
| Ultralytics | 8.0+ | YOLOv8官方库 |
| Flask | 3.0+ | Web框架 |
| OpenCV | 4.8+ | 图像处理 |
| FastAPI | 0.100+ | API框架 |
| Pillow | 10.0+ | 图像库 |

## 依赖安装

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

**国内镜像**（如果下载慢）:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 快速启动

### 方式1: 使用启动脚本（推荐）
```bash
./start.sh
```

### 方式2: 直接运行
```bash
python yolo_training_system_v2.py  # 专业版
```

## 数据存储

所有数据保存在 `yolo_workspace/` 目录：

```
yolo_workspace/
├── dataset/                # 数据集
│   ├── images/
│   │   ├── train/         # 训练集图片
│   │   └── val/           # 验证集图片
│   ├── labels/
│   │   ├── train/         # 训练集标注
│   │   └── val/           # 验证集标注
│   └── data.yaml          # 数据配置
│
├── models/                 # 训练的模型
│   └── runs/detect/
│       └── [实验名称]/
│           └── weights/
│               └── best.pt
│
└── classes.json            # 类别配置
```

## 端口使用

| 端口 | 服务 | 说明 |
|------|------|------|
| 7865 | 专业版训练系统 | 完整功能 + 高级参数 |
| 7864 | 基础版训练系统 | 简化版 |
| 7863 | 简洁检测界面 | 只检测不训练 |
| 8000 | REST API | 提供API接口 |

## 常见问题

### Q1: 如何切换GPU/CPU？
在代码中修改 `device='cpu'` 为 `device='cuda'`

### Q2: 如何添加新的预训练模型？
将 `.pt` 文件放在项目根目录，测试时会自动识别

### Q3: 训练数据保存在哪里？
`yolo_workspace/dataset/` 目录

### Q4: 如何导出模型？
```python
from ultralytics import YOLO
model = YOLO('best.pt')
model.export(format='onnx')  # 或 'coreml', 'tflite'
```

## 开发计划

- [ ] 添加TensorBoard可视化
- [ ] 支持视频检测
- [ ] 模型对比功能
- [ ] 数据集导入导出
- [ ] 训练进度实时显示
- [ ] 多GPU并行训练

## 贡献指南

欢迎提交Issue和PR！

### 提交代码
1. Fork本项目
2. 创建新分支 (`git checkout -b feature/xxx`)
3. 提交代码 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0 (2025-12-03)
- ✅ 初始版本发布
- ✅ 完整的训练流程
- ✅ 内置标注工具
- ✅ 20+训练参数
- ✅ 模型选择功能
- ✅ REST API支持

## 联系方式

- 项目地址: GitHub (待添加)
- 问题反馈: Issues
- 文档: 查看 README.md

---

**最后更新**: 2025-12-03
**维护者**: 项目团队
