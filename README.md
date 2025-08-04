# VidVault 🎥

一个现代化的视频下载工具，支持从YouTube等平台下载视频和音频文件。

![VidVault](https://img.shields.io/badge/VidVault-Video%20Downloader-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18.2.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green)

## ✨ 功能特性

- 🎬 **多平台支持**: 支持YouTube、Bilibili等主流视频平台
- 📹 **视频下载**: 支持多种格式和质量选择
- 🎵 **音频提取**: 一键提取MP3音频文件
- ⚡ **实时进度**: 实时显示下载进度和状态
- 🎨 **现代UI**: 基于Material-UI的现代化界面
- 🔧 **易于使用**: 一键启动，简单操作
- 📱 **响应式设计**: 支持桌面和移动设备

## 🏗️ 技术栈

### 后端
- **Python 3.8+** - 主要编程语言
- **FastAPI** - 现代化Web框架
- **yt-dlp** - 强大的视频下载引擎
- **Uvicorn** - ASGI服务器

### 前端
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Material-UI** - 现代化UI组件库
- **Axios** - HTTP客户端

## 🚀 快速开始

### 一键启动

```bash
# 克隆项目
git clone https://github.com/LoPolyDragon/VidVault.git
cd VidVault

# 启动服务
./start.sh
```

### 手动安装

#### 1. 安装后端依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install fastapi uvicorn yt-dlp
```

#### 2. 安装前端依赖

```bash
cd frontend
npm install
```

#### 3. 启动服务

```bash
# 启动后端 (端口 8000)
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端 (端口 3000)
cd frontend
npm start
```

## 📖 使用方法

1. **启动应用**: 运行 `./start.sh`
2. **打开浏览器**: 访问 http://localhost:3000
3. **输入视频URL**: 粘贴YouTube等平台的视频链接
4. **获取视频信息**: 点击"获取视频信息"查看详情
5. **选择下载类型**: 选择视频或音频格式
6. **开始下载**: 点击"开始下载"按钮
7. **下载完成**: 点击"下载文件"保存到本地

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📋 API接口

### 获取视频信息
```http
POST /api/video/info
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

### 开始下载
```http
POST /api/video/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "download_type": "video",
  "format": "best",
  "quality": "best"
}
```

### 获取下载状态
```http
GET /api/video/status/{download_id}
```

### 下载文件
```http
GET /api/video/download/{download_id}
```

## 🛠️ 管理命令

```bash
# 启动服务
./start.sh

# 停止服务
./stop.sh

# 查看状态
./start.sh status

# 获取帮助
./start.sh help
```

## 📁 项目结构

```
VidVault/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI主程序
│   ├── video_processor.py  # 视频处理模块
│   ├── download_manager.py # 下载管理模块
│   └── downloads/          # 下载文件存储
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── App.tsx        # 主应用组件
│   │   ├── components/    # React组件
│   │   └── index.tsx      # 应用入口
│   └── package.json       # 前端依赖配置
├── start.sh               # 启动脚本
├── stop.sh                # 停止脚本
└── README.md              # 项目说明
```

## 🔧 配置选项

### 下载选项
- `download_type`: `video` | `audio` - 下载类型
- `format`: `best` | `worst` | `mp4` | `webm` - 视频格式
- `quality`: `best` | `worst` | `720p` | `1080p` - 视频质量
- `start_time`: 开始时间（秒）
- `end_time`: 结束时间（秒）

## 🐛 故障排除

### 端口被占用
```bash
# 清理端口
lsof -ti :8000 | xargs kill -9  # 后端端口
lsof -ti :3000 | xargs kill -9  # 前端端口
```

### 依赖问题
```bash
# 重新安装后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重新安装前端依赖
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 权限问题
```bash
chmod +x start.sh stop.sh
```

## 📝 日志查看

```bash
# 后端日志
tail -f backend/backend.log

# 前端日志
tail -f frontend/frontend.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载引擎
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Material-UI](https://mui.com/) - React UI组件库

## 📞 联系方式

- 项目主页: https://github.com/LoPolyDragon/VidVault
- 问题反馈: [Issues](https://github.com/LoPolyDragon/VidVault/issues)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！ 