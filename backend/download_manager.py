import asyncio
import os
import uuid
from typing import Dict, Any, Optional
import yt_dlp
from datetime import datetime

class DownloadManager:
    def __init__(self):
        self.downloads: Dict[str, Dict[str, Any]] = {}
        self.download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def _progress_hook(self, download_id: str):
        """为特定下载ID创建进度钩子"""
        def hook(d):
            if download_id not in self.downloads:
                return

            status = d['status']
            
            if status == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                speed = d.get('speed', 0) or 0
                eta = d.get('eta', 0) or 0

                if total_bytes and total_bytes > 0:
                    progress = (downloaded_bytes / total_bytes) * 100
                else:
                    progress = 0

                self.downloads[download_id].update({
                    'progress': round(progress, 2),
                    'speed': speed,
                    'eta': eta,
                    'downloaded_bytes': downloaded_bytes,
                    'total_bytes': total_bytes,
                    'status': 'downloading'
                })
                print(f"DEBUG: Progress update for {download_id}: {progress:.1f}%")

            elif status == 'finished':
                # 保留最后的字节信息
                current_status = self.downloads[download_id]
                self.downloads[download_id].update({
                    'progress': 100,
                    'status': 'finished',
                    'speed': 0,
                    'eta': 0,
                    'downloaded_bytes': current_status.get('downloaded_bytes', 0),
                    'total_bytes': current_status.get('total_bytes', 0)
                })
                print(f"DEBUG: Download finished for {download_id}")

            elif status == 'error':
                error_msg = str(d.get('error', 'Unknown error'))
                self.downloads[download_id].update({
                    'status': 'error',
                    'error': error_msg,
                    'progress': 0
                })
                print(f"DEBUG: Download error for {download_id}: {error_msg}")

        return hook

    async def start_download(self, url: str, options: Dict[str, Any]) -> str:
        """开始下载任务"""
        download_id = str(uuid.uuid4())
        
        # 初始化下载记录
        self.downloads[download_id] = {
            'status': 'starting',
            'progress': 0,
            'speed': 0,
            'eta': 0,
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'error': '',
            'title': '',
            'output_path': '',
            'start_time': datetime.now().isoformat(),
            'url': url,
            'options': options
        }

        # 根据下载类型选择格式
        download_type = options.get('download_type', 'video')
        format_preference = options.get('format', 'best')
        
        if download_type == 'audio':
            format_str = 'bestaudio/best'
        elif download_type == 'full':
            format_str = 'bestvideo+bestaudio/best'
        else:
            # 对于所有视频下载，使用这个通用格式
            format_str = 'bestvideo+bestaudio/best'

        # 设置输出格式和文件名
        if download_type == 'audio':
            outtmpl = os.path.join(self.download_dir, '%(title)s_%(uploader)s.%(ext)s')
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # 对于视频，使用更简单的方法：直接指定mp4格式
            outtmpl = os.path.join(self.download_dir, '%(title)s_%(uploader)s.%(ext)s')
            # 优先选择mp4格式
            format_str = 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            postprocessors = []

        # 使用更完整的配置来绕过 403 错误
        ydl_opts = {
            'format': format_str,
            'progress_hooks': [self._progress_hook(download_id)],
            'quiet': True,
            'no_warnings': True,
            'outtmpl': outtmpl,
            'postprocessors': postprocessors,
            # 添加用户代理来绕过 403 错误
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # 添加其他反检测配置
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_color': True,
            # 添加更多反检测选项
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retries': 3,
            'file_access_retries': 3,
            # 添加HLS流支持
            'hls_prefer_native': True,
            'hls_use_mpegts': False,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'live'],
                }
            },
        }

        # 在后台运行下载任务
        asyncio.create_task(self._download_task(download_id, url, ydl_opts))
        
        return download_id

    async def _download_task(self, download_id: str, url: str, ydl_opts: Dict):
        """异步下载任务"""
        try:
            print(f"DEBUG: Starting download for {download_id} with options: {ydl_opts}")
            
            # 立即更新状态为正在处理
            self.downloads[download_id].update({
                'status': 'processing'
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"DEBUG: Created YoutubeDL instance for {download_id}")
                
                # 获取视频信息
                print(f"DEBUG: Extracting info for {download_id}")
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                
                if not info:
                    raise Exception("无法获取视频信息")
                
                print(f"DEBUG: Got info for {download_id}: {info.get('title', 'No title')}")
                
                # 获取文件信息用于状态更新
                title = info.get('title', 'unknown_video')
                print(f"DEBUG: Got video title for {download_id}: {title}")

                # 开始下载
                print(f"DEBUG: Starting actual download for {download_id}")
                await asyncio.to_thread(ydl.download, [url])
                print(f"DEBUG: Download completed for {download_id}")

                # 更新下载信息 - 查找实际下载的文件
                download_dir_files = os.listdir(self.download_dir)
                # 找到最新的文件
                latest_file = None
                latest_time = 0
                for filename in download_dir_files:
                    file_path = os.path.join(self.download_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = os.path.getmtime(file_path)
                        if file_time > latest_time:
                            latest_time = file_time
                            latest_file = file_path
                
                self.downloads[download_id].update({
                    'output_path': latest_file or '',
                    'title': title,
                    'status': 'finished'
                })

        except Exception as e:
            error_msg = str(e)
            print(f"Download error for {download_id}: {error_msg}")
            self.downloads[download_id].update({
                'status': 'error',
                'error': error_msg,
                'progress': 0
            })

    def get_download_status(self, download_id: str) -> Optional[Dict[str, Any]]:
        """获取下载状态"""
        return self.downloads.get(download_id)

    def get_all_downloads(self) -> Dict[str, Dict[str, Any]]:
        """获取所有下载记录"""
        return self.downloads

    def cancel_download(self, download_id: str) -> bool:
        """取消下载（这里简单实现为标记状态）"""
        if download_id in self.downloads:
            self.downloads[download_id]['status'] = 'cancelled'
            return True
        return False

    def _get_download_path(self, title: str, ext: str) -> str:
        """生成安全的下载路径"""
        # 清理文件名中的非法字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_title:
            safe_title = "download"
        
        filename = f"{safe_title}.{ext}"
        return os.path.join(self.download_dir, filename)