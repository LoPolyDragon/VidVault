import yt_dlp
from typing import Dict, Any, Optional
import re

class VideoProcessor:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            # 添加用户代理来绕过 403 错误
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_color': True,
        }

    def _is_valid_url(self, url: str) -> bool:
        # 简单的 URL 验证
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """获取视频信息"""
        if not self._is_valid_url(url):
            raise ValueError("Invalid URL format")

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 使用 asyncio.to_thread 来避免阻塞
                import asyncio
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                
                if not info:
                    return None

                # 提取关键信息
                result = {
                    'title': info.get('title', 'Unknown'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'formats': []
                }

                # 处理格式信息
                formats = info.get('formats', [])
                for fmt in formats[:10]:  # 只返回前10个格式以避免响应过大
                    format_info = {
                        'format_id': fmt.get('format_id', ''),
                        'ext': fmt.get('ext', ''),
                        'resolution': fmt.get('resolution', 'N/A'),
                        'filesize': fmt.get('filesize'),
                        'vcodec': fmt.get('vcodec', 'N/A'),
                        'acodec': fmt.get('acodec', 'N/A'),
                    }
                    result['formats'].append(format_info)

                return result

        except Exception as e:
            print(f"Error getting video info: {e}")
            raise e

    def get_supported_sites(self) -> list:
        """获取支持的网站列表"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.list_extractors()
        except Exception as e:
            print(f"Error getting supported sites: {e}")
            return []