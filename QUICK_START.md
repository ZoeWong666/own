# 🚀 快速开始

## 5分钟上手指南

### 1. 安装环境

```bash
# 进入项目目录
cd yolo-training-system

# 创建虚拟环境
python3 -m venv venv

# 激活环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动系统

#### 方式A: 使用启动脚本（推荐）
```bash
./start.sh
```
然后选择对应的功能即可。

#### 方式B: 直接运行
```bash
# 专业版（推荐）
python yolo_training_system_v2.py

# 基础版
python yolo_training_system.py

# 简洁检测
python simple_web_app.py

# API服务
python detection_api.py
```

### 3. 打开浏览器

- 专业版: http://localhost:7865
- 基础版: http://localhost:7864
- 简洁版: http://localhost:7863
- API文档: http://localhost:8000/docs

### 4. 开始使用

#### 第一步：设置类别
1. 点击"1. 设置类别"标签
2. 输入类别名称，例如：`person`
3. 点击"添加类别"
4. 重复添加其他类别：`car`, `dog`, `cat`, `chair`

#### 第二步：标注数据
1. 点击"2. 标注数据"标签
2. 选择"训练集"
3. 点击"上传图片"，选择图片
4. 在图片上拖动鼠标框选物体
5. 输入类别ID（0表示第一个类别）
6. 点击"保存标注"

**建议**:
- 每个类别至少100张图片
- 80%放训练集，20%放验证集

#### 第三步：训练模型
1. 点击"3. 开始训练"标签
2. 选择模型大小（初学者选Nano）
3. 设置训练轮数（建议100）
4. 调整其他参数（可选）
5. 点击"开始训练"

**注意**: CPU训练较慢，建议使用GPU。

#### 第四步：测试模型
1. 点击"4. 测试模型"标签
2. 从下拉框选择训练好的模型
3. 上传测试图片
4. 点击"开始检测"
5. 查看结果

## 常见问题

### Q: 安装依赖失败？
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 启动失败？
- 检查端口是否被占用
- 确认虚拟环境已激活
- 查看错误日志

### Q: 显存不足？
- 减小batch_size（从16改为8或4）
- 使用更小的模型（Nano）
- 减小图片尺寸（从640改为320）

### Q: 如何使用GPU？
需要安装CUDA版本的PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 数据集位置

所有数据保存在：
```
yolo_workspace/
├── dataset/          # 数据集
│   ├── images/      # 图片
│   └── labels/      # 标注
├── models/          # 训练的模型
└── classes.json     # 类别配置
```

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 查看 [API_GUIDE.md](API_GUIDE.md) 学习API使用
- 访问 [YOLOv8官方文档](https://docs.ultralytics.com/)

**祝你训练顺利！🎯**
