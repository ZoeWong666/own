# YOLOv8 训练系统 - 桌面客户端

## 概述

已将原来的 Web 应用封装为真正的桌面客户端,不再需要浏览器,提供更好的用户体验。

### 技术方案

- **PyWebView**: 使用系统原生 WebView 渲染界面
- **Flask**: 后端服务保持不变
- **PyInstaller**: 打包成独立可执行文件

### 优势

✅ **无需浏览器**: 原生桌面窗口,不会打开浏览器
✅ **体积适中**: 约 20-30MB (不含深度学习模型)
✅ **跨平台**: 支持 Windows、macOS、Linux
✅ **简单易用**: 双击即可运行,无需配置环境
✅ **更好体验**: 窗口大小可调,支持关闭确认

## 运行方式

### 开发模式 (需要 Python 环境)

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行桌面客户端:
```bash
python3 desktop_launcher.py
```

或使用启动脚本:
```bash
./start_desktop.sh
```

### 打包成可执行文件

1. 运行打包脚本:
```bash
./build_desktop.sh
```

2. 打包完成后,可执行文件位于:
```
dist/YOLOv8训练系统/YOLOv8训练系统
```

3. 分发:
- macOS: `dist/YOLOv8训练系统-macOS.zip`
- Windows: 在 Windows 上打包会生成 `.exe` 文件
- Linux: 在 Linux 上打包会生成对应的可执行文件

## 文件说明

### 新增文件

- `desktop_launcher.py` - 桌面客户端启动器
- `desktop_system.spec` - PyInstaller 桌面版配置
- `build_desktop.sh` - 桌面版打包脚本
- `start_desktop.sh` - 桌面版快速启动脚本

### 原有文件 (依然可用)

- `launcher.py` - 原 Web 版启动器 (自动打开浏览器)
- `yolo_system.spec` - PyInstaller Web 版配置
- `build.sh` - Web 版打包脚本
- `start.sh` - Web 版快速启动脚本

## 两种模式对比

| 特性 | Web 模式 (launcher.py) | 桌面模式 (desktop_launcher.py) |
|------|----------------------|------------------------------|
| 界面 | 自动打开浏览器 | 原生桌面窗口 |
| 体验 | 浏览器标签页 | 独立应用窗口 |
| 打包大小 | 较小 | 稍大 (增加 pywebview) |
| 控制台 | 显示 | 可隐藏 |
| 适用场景 | 开发调试 | 最终用户 |

## 打包配置

### macOS

默认配置即可,会自动处理 macOS 特有的依赖:
- pyobjc-core
- pyobjc-framework-Cocoa
- pyobjc-framework-WebKit

### Windows

需要在 Windows 系统上打包。PyWebView 会自动使用 Windows 的 WebView2。

### Linux

需要安装系统依赖:
```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0

# Fedora
sudo dnf install python3-gobject gtk3 webkit2gtk3
```

## 窗口配置

可以在 `desktop_launcher.py` 中修改窗口属性:

```python
window = webview.create_window(
    title='YOLOv8 训练系统',      # 窗口标题
    url='http://127.0.0.1:7865',   # 服务地址
    width=1280,                     # 窗口宽度
    height=800,                     # 窗口高度
    resizable=True,                 # 允许调整大小
    fullscreen=False,               # 全屏模式
    min_size=(800, 600),           # 最小尺寸
    confirm_close=True              # 关闭确认
)
```

## 常见问题

### Q: 能否不显示控制台窗口?

A: 可以,在 `desktop_system.spec` 中设置:
```python
console=False  # 不显示控制台
```

### Q: 如何添加应用图标?

A: 在 `desktop_system.spec` 中设置:
```python
icon='path/to/icon.icns'  # macOS
icon='path/to/icon.ico'   # Windows
```

### Q: 桌面版和 Web 版可以共存吗?

A: 可以!两者使用不同的启动文件和配置文件,互不影响。

### Q: 打包后文件很大怎么办?

A: 主要是深度学习模型占用空间。可以考虑:
1. 不打包模型,首次运行时自动下载
2. 使用模型压缩技术
3. 提供模型单独下载

## 后续改进建议

1. **添加应用图标**: 设计并添加自定义图标
2. **优化启动速度**: 使用启动画面,预加载模型
3. **自动更新**: 添加版本检查和自动更新功能
4. **系统托盘**: 添加系统托盘支持,最小化到托盘
5. **菜单栏**: 添加原生菜单栏 (文件、编辑、帮助等)
6. **拖放支持**: 支持拖拽图片到窗口进行检测

## 许可证

与主项目保持一致
