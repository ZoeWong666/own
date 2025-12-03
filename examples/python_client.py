"""
Python客户端示例 - 如何使用YOLO训练系统API
"""
import requests
from pathlib import Path
from PIL import Image
import io


class YOLOClient:
    """YOLO API客户端"""

    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url

    def health_check(self):
        """健康检查"""
        response = requests.get(f'{self.base_url}/health')
        return response.json()

    def detect(self, image_path, conf=0.25, iou=0.45):
        """
        检测单张图片

        Args:
            image_path: 图片路径
            conf: 置信度阈值 (0-1)
            iou: IoU阈值 (0-1)

        Returns:
            检测结果字典
        """
        with open(image_path, 'rb') as f:
            response = requests.post(
                f'{self.base_url}/detect',
                files={'image': f},
                data={
                    'conf_threshold': conf,
                    'iou_threshold': iou
                }
            )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'检测失败: {response.status_code}')

    def detect_batch(self, image_paths, conf=0.25):
        """
        批量检测

        Args:
            image_paths: 图片路径列表
            conf: 置信度阈值

        Returns:
            批量检测结果
        """
        files = [('images', open(p, 'rb')) for p in image_paths]

        try:
            response = requests.post(
                f'{self.base_url}/detect_batch',
                files=files,
                data={'conf_threshold': conf}
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'批量检测失败: {response.status_code}')
        finally:
            # 关闭所有文件
            for _, f in files:
                f.close()

    def get_annotated_image(self, image_path, output_path=None):
        """
        获取带标注框的图片

        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（可选）

        Returns:
            PIL Image对象
        """
        with open(image_path, 'rb') as f:
            response = requests.post(
                f'{self.base_url}/detect_annotated',
                files={'image': f}
            )

        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))

            if output_path:
                img.save(output_path)

            return img
        else:
            raise Exception(f'获取标注图片失败: {response.status_code}')


def example_1_simple_detection():
    """示例1: 简单检测"""
    print("=" * 60)
    print("示例1: 简单检测")
    print("=" * 60)

    client = YOLOClient()

    # 检查服务状态
    health = client.health_check()
    print(f"服务状态: {health}")

    # 检测图片（请替换为你的图片路径）
    result = client.detect('test.jpg', conf=0.25)

    print(f"\n检测到 {result['count']} 个物体:")
    for det in result['detections']:
        print(f"  - {det['class_name']}: {det['confidence']:.2%} at {det['bbox']}")


def example_2_batch_detection():
    """示例2: 批量检测"""
    print("\n" + "=" * 60)
    print("示例2: 批量检测")
    print("=" * 60)

    client = YOLOClient()

    # 批量检测多张图片
    image_paths = ['img1.jpg', 'img2.jpg', 'img3.jpg']

    results = client.detect_batch(image_paths, conf=0.3)

    print(f"\n总共处理: {results['total_images']} 张图片")
    print(f"检测到: {results['total_detections']} 个物体\n")

    for result in results['results']:
        print(f"📷 {result['filename']}: {result['count']} 个物体")


def example_3_annotated_image():
    """示例3: 获取标注图片"""
    print("\n" + "=" * 60)
    print("示例3: 获取标注图片")
    print("=" * 60)

    client = YOLOClient()

    # 获取标注后的图片
    img = client.get_annotated_image('test.jpg', 'result.jpg')

    print(f"✓ 标注图片已保存: result.jpg")
    print(f"  图片大小: {img.size}")


def example_4_confidence_threshold():
    """示例4: 调整置信度阈值"""
    print("\n" + "=" * 60)
    print("示例4: 不同置信度阈值对比")
    print("=" * 60)

    client = YOLOClient()

    for conf in [0.1, 0.25, 0.5, 0.75]:
        result = client.detect('test.jpg', conf=conf)
        print(f"置信度 {conf}: 检测到 {result['count']} 个物体")


def example_5_filter_by_class():
    """示例5: 按类别过滤"""
    print("\n" + "=" * 60)
    print("示例5: 按类别过滤检测结果")
    print("=" * 60)

    client = YOLOClient()

    result = client.detect('test.jpg', conf=0.25)

    # 只显示"person"类别
    persons = [d for d in result['detections'] if d['class_name'] == 'person']
    print(f"检测到 {len(persons)} 个人")

    # 统计每个类别的数量
    from collections import Counter
    class_counts = Counter([d['class_name'] for d in result['detections']])

    print("\n类别统计:")
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count}")


def example_6_error_handling():
    """示例6: 错误处理"""
    print("\n" + "=" * 60)
    print("示例6: 错误处理")
    print("=" * 60)

    client = YOLOClient()

    try:
        result = client.detect('non_existent.jpg')
        print(f"检测成功: {result['count']} 个物体")
    except FileNotFoundError:
        print("❌ 错误: 文件不存在")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    print("\n🎯 YOLO API 使用示例")
    print("=" * 60)
    print("请确保:")
    print("1. API服务已启动 (python detection_api.py)")
    print("2. 有测试图片 (test.jpg, img1.jpg等)")
    print("=" * 60)

    try:
        # 运行所有示例
        example_1_simple_detection()
        # example_2_batch_detection()
        # example_3_annotated_image()
        # example_4_confidence_threshold()
        # example_5_filter_by_class()
        # example_6_error_handling()

    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        print("\n提示:")
        print("  1. 确保API服务已启动")
        print("  2. 检查图片路径是否正确")
        print("  3. 确保模型文件存在")
