# -*- coding: utf-8 -*-
"""
YOLOv8 目标检测 FastAPI 接口
提供：图片上传 → 检测多个物体 → 返回位置+类别
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io
import numpy as np
import cv2
from typing import Optional
import base64

app = FastAPI(
    title="YOLOv8 目标检测 API",
    description="检测图片中的多个物体，返回位置和类别",
    version="1.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局模型实例
model = None
model_path = "yolov8n.pt"

def load_model(path: str = "yolov8n.pt"):
    """加载 YOLO 模型"""
    global model, model_path
    model = YOLO(path)
    model_path = path
    return model

# 启动时加载模型
@app.on_event("startup")
async def startup_event():
    """启动时加载默认模型"""
    print("正在加载 YOLOv8 模型...")
    load_model()
    print(f"✓ 模型加载完成: {model_path}")

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "YOLOv8 目标检测 API",
        "version": "1.0.0",
        "model": model_path,
        "endpoints": {
            "/detect": "POST - 检测图片中的物体（返回JSON）",
            "/detect_image": "POST - 检测并返回标注后的图片",
            "/health": "GET - 健康检查",
            "/models": "GET - 查看可用模型",
            "/load_model": "POST - 加载指定模型"
        },
        "example": {
            "curl": "curl -X POST -F 'image=@test.jpg' http://localhost:8000/detect",
            "python": "requests.post('http://localhost:8000/detect', files={'image': open('test.jpg', 'rb')})"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": model_path
    }

@app.post("/detect")
async def detect_objects(
    image: UploadFile = File(..., description="要检测的图片"),
    conf_threshold: float = Form(0.25, description="置信度阈值 (0-1)"),
    iou_threshold: float = Form(0.45, description="IOU阈值 (0-1)"),
    return_image: bool = Form(False, description="是否返回标注后的图片(base64)")
):
    """
    检测图片中的物体

    参数:
    - image: 图片文件
    - conf_threshold: 置信度阈值，低于此值的检测结果会被过滤
    - iou_threshold: IOU阈值，用于非极大值抑制

    返回:
    - detections: 检测结果列表
    - count: 检测到的物体数量
    - image_base64: (可选) 标注后的图片 (base64编码)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="模型未加载")

    try:
        # 读取图片
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')

        # 进行检测
        results = model.predict(
            img,
            conf=conf_threshold,
            iou=iou_threshold,
            verbose=False
        )[0]

        # 提取检测结果
        detections = []
        boxes = results.boxes

        for i, box in enumerate(boxes):
            # 获取边界框坐标
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            # 获取置信度
            conf = float(box.conf[0])
            # 获取类别
            cls = int(box.cls[0])
            class_name = results.names[cls]

            detections.append({
                'id': i + 1,
                'class': class_name,
                'confidence': round(conf, 4),
                'bbox': {
                    'x1': round(float(x1), 2),
                    'y1': round(float(y1), 2),
                    'x2': round(float(x2), 2),
                    'y2': round(float(y2), 2),
                    'width': round(float(x2 - x1), 2),
                    'height': round(float(y2 - y1), 2)
                }
            })

        response = {
            'success': True,
            'count': len(detections),
            'detections': detections,
            'image_size': {
                'width': img.width,
                'height': img.height
            },
            'parameters': {
                'conf_threshold': conf_threshold,
                'iou_threshold': iou_threshold
            }
        }

        # 如果需要返回标注后的图片
        if return_image:
            annotated_img = results.plot()
            # 转换为 base64
            _, buffer = cv2.imencode('.jpg', annotated_img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            response['image_base64'] = img_base64

        return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.post("/detect_image")
async def detect_and_return_image(
    image: UploadFile = File(...),
    conf_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45)
):
    """
    检测图片并直接返回标注后的图片

    返回: 标注后的图片 (JPEG格式)
    """
    if model is None:
        raise HTTPException(status_code=500, detail="模型未加载")

    try:
        # 读取图片
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')

        # 进行检测
        results = model.predict(
            img,
            conf=conf_threshold,
            iou=iou_threshold,
            verbose=False
        )[0]

        # 获取标注后的图片
        annotated_img = results.plot()

        # 转换为字节流
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_bytes = io.BytesIO(buffer.tobytes())

        return StreamingResponse(
            img_bytes,
            media_type="image/jpeg",
            headers={"Content-Disposition": "inline; filename=detected.jpg"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.post("/detect_batch")
async def detect_batch(
    images: list[UploadFile] = File(..., description="多张图片"),
    conf_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45)
):
    """
    批量检测多张图片

    返回: 每张图片的检测结果
    """
    if model is None:
        raise HTTPException(status_code=500, detail="模型未加载")

    results = []

    for i, image_file in enumerate(images):
        try:
            # 读取图片
            contents = await image_file.read()
            img = Image.open(io.BytesIO(contents)).convert('RGB')

            # 进行检测
            detection_results = model.predict(
                img,
                conf=conf_threshold,
                iou=iou_threshold,
                verbose=False
            )[0]

            # 提取检测结果
            detections = []
            boxes = detection_results.boxes

            for j, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = detection_results.names[cls]

                detections.append({
                    'id': j + 1,
                    'class': class_name,
                    'confidence': round(conf, 4),
                    'bbox': {
                        'x1': round(float(x1), 2),
                        'y1': round(float(y1), 2),
                        'x2': round(float(x2), 2),
                        'y2': round(float(y2), 2)
                    }
                })

            results.append({
                'image_index': i,
                'image_name': image_file.filename,
                'count': len(detections),
                'detections': detections
            })

        except Exception as e:
            results.append({
                'image_index': i,
                'image_name': image_file.filename,
                'error': str(e)
            })

    return JSONResponse(content={
        'success': True,
        'total_images': len(images),
        'results': results
    })

@app.get("/models")
async def list_models():
    """列出可用的模型"""
    return {
        "current_model": model_path,
        "available_models": [
            {
                "name": "yolov8n.pt",
                "size": "6MB",
                "mAP": "37.3",
                "speed": "最快",
                "description": "纳米版，适合边缘设备"
            },
            {
                "name": "yolov8s.pt",
                "size": "22MB",
                "mAP": "44.9",
                "speed": "快",
                "description": "小型版，平衡速度和精度"
            },
            {
                "name": "yolov8m.pt",
                "size": "52MB",
                "mAP": "50.2",
                "speed": "中等",
                "description": "中型版，服务器部署"
            },
            {
                "name": "yolov8l.pt",
                "size": "87MB",
                "mAP": "52.9",
                "speed": "慢",
                "description": "大型版，高精度"
            },
            {
                "name": "yolov8x.pt",
                "size": "136MB",
                "mAP": "53.9",
                "speed": "最慢",
                "description": "超大版，最高精度"
            }
        ]
    }

@app.post("/load_model")
async def load_model_endpoint(model_name: str = Form(...)):
    """加载指定的模型"""
    try:
        load_model(model_name)
        return {
            "success": True,
            "message": f"模型 {model_name} 加载成功",
            "current_model": model_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载模型失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    print("""
╔══════════════════════════════════════════════════════════════════╗
║           YOLOv8 目标检测 API 服务器                             ║
╚══════════════════════════════════════════════════════════════════╝

🚀 启动地址: http://localhost:8000
📖 API文档: http://localhost:8000/docs
🔍 交互式文档: http://localhost:8000/redoc

测试命令:
  curl -X POST -F "image=@test.jpg" http://localhost:8000/detect

Python示例:
  import requests
  with open('test.jpg', 'rb') as f:
      response = requests.post(
          'http://localhost:8000/detect',
          files={'image': f}
      )
  print(response.json())
    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
