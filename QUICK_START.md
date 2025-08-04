# VidVault 快速启动指南

## 🚀 一键启动

```bash
./start.sh
```

## 🛑 停止服务

```bash
./stop.sh
```

或者

```bash
./start.sh stop
```

## 📊 检查状态

```bash
./start.sh status
```

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000

## 📋 使用方法

1. 启动服务：`./start.sh`
2. 打开浏览器访问：http://localhost:3000
3. 输入视频URL（支持YouTube等平台）
4. 点击"获取视频信息"查看视频详情
5. 选择下载类型（视频/音频）
6. 点击"开始下载"
7. 等待下载完成，点击"下载文件"保存到本地

## 🔧 支持的功能

- ✅ YouTube视频下载
- ✅ MP4格式输出
- ✅ MP3音频提取
- ✅ 实时下载进度
- ✅ 视频信息预览
- ✅ 多种质量选择

## 📝 日志查看

```bash
# 实时查看后端日志
tail -f backend/backend.log

# 实时查看前端日志
tail -f frontend/frontend.log
```

## ❓ 故障排除

### 端口被占用
```bash
# 手动清理端口
lsof -ti :8000 | xargs kill -9  # 清理后端
lsof -ti :3000 | xargs kill -9  # 清理前端
```

### 依赖问题
```bash
# 重新安装后端依赖
cd backend
source venv/bin/activate
pip install fastapi uvicorn yt-dlp

# 重新安装前端依赖
cd frontend
npm install
```

### 权限问题
```bash
chmod +x start.sh stop.sh
```

## 🆘 获取帮助

```bash
./start.sh help
```