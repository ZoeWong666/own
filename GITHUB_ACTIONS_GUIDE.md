# 🚀 GitHub Actions 自动打包指南

## 📦 功能说明

使用 GitHub Actions 在云端自动打包 Windows、macOS、Linux 三个平台的可执行文件。

## ✨ 优势

- ✅ **完全免费**：GitHub Actions 对公开仓库免费
- ✅ **自动化**：推送代码自动打包
- ✅ **多平台**：同时打包三个平台
- ✅ **无需本地环境**：在云端完成所有工作

## 🎯 使用步骤

### 1. 推送代码到 GitHub

```bash
# 如果还没有推送
git add .
git commit -m "Add GitHub Actions workflow"
git push origin main
```

### 2. 触发打包

有两种方式触发打包：

#### 方式 A：创建版本标签（推荐）

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

这会触发打包并自动创建 GitHub Release。

#### 方式 B：手动触发

1. 访问你的 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Build Executables"
4. 点击 "Run workflow"
5. 点击绿色的 "Run workflow" 按钮

### 3. 下载打包结果

#### 如果使用标签触发：

1. 访问仓库的 "Releases" 页面
2. 找到你的版本（如 v1.0.0）
3. 下载对应平台的压缩包：
   - `YOLOv8训练系统-Windows.zip` ← **Windows .exe**
   - `YOLOv8训练系统-macOS.zip`
   - `YOLOv8训练系统-Linux.tar.gz`

#### 如果手动触发：

1. 在 "Actions" 页面查看构建进度
2. 构建完成后，点击对应的 workflow
3. 在 "Artifacts" 部分下载文件

---

## 📋 详细流程图

```
你推送代码/创建标签
    ↓
GitHub Actions 自动开始
    ↓
├─ Windows 机器打包 → YOLOv8训练系统.exe
├─ macOS 机器打包   → YOLOv8训练系统 (macOS)
└─ Linux 机器打包   → YOLOv8训练系统 (Linux)
    ↓
自动上传到 Release
    ↓
你下载并分发给用户
```

---

## ⏱️ 预计时间

- Windows 打包：15-20 分钟
- macOS 打包：15-20 分钟
- Linux 打包：10-15 分钟

总计约 40-55 分钟（并行执行）

---

## 💰 费用说明

### 免费配额（公开仓库）

GitHub 为公开仓库提供：
- ✅ 无限分钟数
- ✅ 完全免费

### 私有仓库

每月免费配额：
- 2,000 分钟（Linux）
- 1,000 分钟（Windows）
- 500 分钟（macOS）

超出后按分钟计费：
- Linux: $0.008/分钟
- Windows: $0.016/分钟
- macOS: $0.08/分钟

**建议：使用公开仓库即可完全免费！**

---

## 🔧 高级配置

### 仅打包 Windows

如果只需要 Windows .exe，编辑 `.github/workflows/build.yml`，删除 `build-macos` 和 `build-linux` 部分。

### 修改触发条件

```yaml
# 推送到 main 分支时触发
on:
  push:
    branches:
      - main

# 每天自动打包一次
on:
  schedule:
    - cron: '0 0 * * *'
```

### 添加构建通知

在 workflow 最后添加：

```yaml
- name: Send notification
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
```

---

## 🐛 常见问题

### Q: Actions 构建失败？

**检查：**
1. `requirements.txt` 是否正确
2. Python 版本是否兼容
3. 查看构建日志

### Q: 下载的文件无法运行？

**Windows：**
- 解压完整文件夹
- 检查 Windows Defender

**macOS：**
```bash
xattr -cr "YOLOv8训练系统"
```

### Q: 如何加速构建？

1. 使用缓存：
```yaml
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

2. 只打包需要的平台

---

## 📖 完整示例

### 发布 v1.0.0 版本

```bash
# 1. 确保代码已提交
git add .
git commit -m "Release v1.0.0"
git push

# 2. 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 3. 等待 40-55 分钟

# 4. 访问 GitHub Releases 页面下载
```

---

## 🎯 最佳实践

### 1. 版本命名规范

使用语义化版本：
- `v1.0.0` - 主版本
- `v1.1.0` - 次版本（新功能）
- `v1.0.1` - 修订版本（bug 修复）

### 2. Release 说明

创建标签时添加详细说明：

```bash
git tag -a v1.0.0 -m "
v1.0.0 Release Notes

Features:
- 新增文件夹批量导入
- 新增自动跳转下一张
- 可配置数据集路径

Bug Fixes:
- 修复标注保存问题

Usage:
1. 解压文件
2. 双击运行
3. 开始使用
"
```

### 3. 定期清理旧版本

保留最近 3-5 个版本，删除过旧的 Release。

---

## 📊 监控构建

### 查看构建状态

添加徽章到 README.md：

```markdown
![Build Status](https://github.com/你的用户名/yolo-training-system/workflows/Build%20Executables/badge.svg)
```

### 构建历史

访问：
```
https://github.com/你的用户名/yolo-training-system/actions
```

---

## 🚀 开始使用

现在就试试：

```bash
git tag v1.0.0
git push origin v1.0.0
```

然后访问你的 GitHub 仓库，在 Actions 页面查看构建进度！

---

## 📝 注意事项

1. **首次构建较慢**：需要下载所有依赖
2. **网络问题**：如果失败，重新运行即可
3. **文件大小**：打包后的文件约 600 MB - 2 GB
4. **Python 版本**：确保与开发环境一致

---

## ✅ 总结

使用 GitHub Actions：
- ✅ 不需要 Windows 机器
- ✅ 不需要虚拟机
- ✅ 完全自动化
- ✅ 免费使用
- ✅ 支持多平台

**推送标签，等待构建，下载分发！**

就这么简单！🎉
