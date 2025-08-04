from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from video_processor import VideoProcessor
from download_manager import DownloadManager

app = FastAPI(title="VidVault API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化处理器
video_processor = VideoProcessor()
download_manager = DownloadManager()

# Pydantic 模型
class VideoInfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    download_type: Optional[str] = "video"
    format: Optional[str] = "best"
    quality: Optional[str] = "best"
    start_time: Optional[int] = None
    end_time: Optional[int] = None

class VideoInfo(BaseModel):
    title: str
    description: str
    duration: int
    thumbnail: str
    uploader: str
    view_count: int
    formats: List[Dict[str, Any]]

# API端点
@app.get("/")
async def root():
    return {"message": "VidVault API is running", "version": "1.0.0"}

@app.post("/api/video/info")
async def get_video_info(request: VideoInfoRequest) -> Dict[str, Any]:
    """获取视频信息"""
    try:
        info = await video_processor.get_video_info(request.url)
        if not info:
            raise HTTPException(status_code=400, detail="无法获取视频信息")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理视频信息时出错: {str(e)}")

@app.post("/api/video/download")
async def start_download(request: DownloadRequest) -> Dict[str, str]:
    """开始下载视频"""
    try:
        options = {
            'download_type': request.download_type,
            'format': request.format,
            'quality': request.quality,
            'start_time': request.start_time,
            'end_time': request.end_time
        }
        
        download_id = await download_manager.start_download(request.url, options)
        return {
            "download_id": download_id,
            "status": "started",
            "message": "下载已开始"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始下载时出错: {str(e)}")

@app.get("/api/video/status/{download_id}")
async def get_download_status(download_id: str) -> Dict[str, Any]:
    """获取下载状态"""
    status = download_manager.get_download_status(download_id)
    if not status:
        raise HTTPException(status_code=404, detail="Download not found")
    return status

@app.get("/api/video/downloads")
async def get_all_downloads() -> List[Dict[str, Any]]:
    """获取所有下载记录"""
    downloads = download_manager.get_all_downloads()
    return [
        {
            "download_id": download_id,
            **download_info
        }
        for download_id, download_info in downloads.items()
    ]

@app.post("/api/video/cancel/{download_id}")
async def cancel_download(download_id: str) -> Dict[str, str]:
    """取消下载"""
    if download_manager.cancel_download(download_id):
        return {"status": "cancelled", "message": "下载已取消"}
    raise HTTPException(status_code=404, detail="Download not found")

@app.get("/api/video/download/{download_id}")
async def download_file(download_id: str):
    """下载完成的文件"""
    print(f"DEBUG: File download requested for ID: {download_id}")
    
    status = download_manager.get_download_status(download_id)
    if not status:
        print(f"DEBUG: Download ID not found: {download_id}")
        raise HTTPException(status_code=404, detail=f"Download not found: {download_id}")
    
    print(f"DEBUG: Download status: {status['status']}")
    
    if status['status'] != 'finished':
        raise HTTPException(status_code=400, detail=f"Download not completed yet, current status: {status['status']}")
    
    file_path = status.get('output_path')
    print(f"DEBUG: File path: {file_path}")
    
    if not file_path:
        raise HTTPException(status_code=404, detail="No output path specified")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Downloaded file not found at path: {file_path}")
    
    filename = os.path.basename(file_path)
    print(f"DEBUG: Serving file: {filename}")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)