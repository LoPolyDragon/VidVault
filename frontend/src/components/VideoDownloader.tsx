import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  LinearProgress,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Chip,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import {
  CloudDownload,
  Info as InfoIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface VideoInfo {
  title: string;
  description: string;
  duration: number;
  thumbnail: string;
  uploader: string;
  view_count: number;
  formats: Array<{
    format_id: string;
    ext: string;
    resolution: string;
    filesize: number | null;
  }>;
}

interface DownloadOptions {
  downloadType: string;
  format: string;
  startTime?: string;
  endTime?: string;
}

interface DownloadStatus {
  status: string;
  progress: number;
  speed: number;
  eta: number;
  downloaded_bytes: number;
  total_bytes: number;
  error: string;
  title: string;
  output_path: string;
}

const VideoDownloader: React.FC = () => {
  const [url, setUrl] = useState<string>('');
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [options, setOptions] = useState<DownloadOptions>({
    downloadType: 'video',
    format: 'best',
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [downloading, setDownloading] = useState<boolean>(false);
  const [downloadId, setDownloadId] = useState<string | null>(null);
  const [downloadStatus, setDownloadStatus] = useState<DownloadStatus | null>(null);

  // 轮询下载状态
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (downloading && downloadId) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/api/video/status/${downloadId}`);
          const status = response.data;
          
          console.log('DEBUG: Status response:', status);
          
          // 确保数据类型正确
          const safeStatus: DownloadStatus = {
            status: status.status || 'unknown',
            progress: Number(status.progress) || 0,
            speed: Number(status.speed) || 0,
            eta: Number(status.eta) || 0,
            downloaded_bytes: Number(status.downloaded_bytes) || 0,
            total_bytes: Number(status.total_bytes) || 0,
            error: status.error || '',
            title: status.title || '',
            output_path: status.output_path || '',
          };
          
          const statusText = safeStatus.status.toLowerCase();
          console.log('DEBUG: Status text:', statusText);

          setDownloadStatus(safeStatus);

          if (statusText === 'finished' || statusText === 'error') {
            setDownloading(false);
            if (statusText === 'error') {
              setError(safeStatus.error || '下载失败');
            } else if (statusText === 'finished') {
              console.log('Download completed successfully!');
              // 可以在这里添加通知或自动下载逻辑
            }
          }
        } catch (err) {
          console.error('DEBUG: polling error:', err);
          setError('获取下载状态失败');
          setDownloading(false);
        }
      }, 2000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [downloading, downloadId]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleGetInfo = async () => {
    if (!url.trim()) {
      setError('请输入视频URL');
      return;
    }

    setLoading(true);
    setError('');
    setVideoInfo(null);

    try {
      const response = await axios.post('http://localhost:8000/api/video/info', {
        url: url.trim()
      });

      setVideoInfo(response.data);
    } catch (error: any) {
      setError('获取视频信息失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!url.trim()) {
      setError('请输入视频URL');
      return;
    }

    try {
      setError('');
      setDownloadStatus(null);
      setDownloading(true);
      
      const response = await axios.post('http://localhost:8000/api/video/download', {
        url: url.trim(),
        download_type: options.downloadType,
        format: options.format,
        start_time: options.startTime ? parseInt(options.startTime) : null,
        end_time: options.endTime ? parseInt(options.endTime) : null,
      });

      if (response.data.download_id) {
        setDownloadId(response.data.download_id);
        console.log('Download started with ID:', response.data.download_id);
        console.log('ID length:', response.data.download_id.length);
      }
    } catch (error: any) {
      console.error('Download error:', error);
      setError('下载失败: ' + (error.response?.data?.detail || error.message));
      setDownloading(false);
    }
  };

  const handleCancel = async () => {
    if (!downloadId) return;

    try {
      const response = await fetch(`http://localhost:8000/api/video/cancel/${downloadId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('取消下载失败');
      }

      setDownloading(false);
      setDownloadStatus(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '取消下载失败');
    }
  };

  const handleDownloadFile = async () => {
    if (!downloadId) return;
    
    try {
      console.log('Downloading file with ID:', downloadId);
      
      // 使用fetch下载文件，避免URL长度限制问题
      const response = await fetch(`http://localhost:8000/api/video/download/${downloadId}`);
      
      if (!response.ok) {
        throw new Error(`下载失败: ${response.status} ${response.statusText}`);
      }
      
      // 获取文件名
      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'downloaded_video.mp4';
      
      if (contentDisposition) {
        const matches = contentDisposition.match(/filename\*?=['"]?([^'";]+)['"]?/);
        if (matches && matches[1]) {
          filename = decodeURIComponent(matches[1]);
        }
      }
      
      // 创建blob并下载
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('File downloaded successfully');
    } catch (error) {
      console.error('Download error:', error);
      setError(`文件下载失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="视频URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="输入YouTube或其他支持的视频URL"
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>下载类型</InputLabel>
              <Select
                value={options.downloadType}
                label="下载类型"
                onChange={(e) => setOptions(prev => ({ ...prev, downloadType: e.target.value }))}
              >
                <MenuItem value="video">视频</MenuItem>
                <MenuItem value="audio">音频</MenuItem>
                <MenuItem value="full">完整质量</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>格式</InputLabel>
              <Select
                value={options.format}
                label="格式"
                onChange={(e) => setOptions(prev => ({ ...prev, format: e.target.value }))}
              >
                <MenuItem value="best">最佳质量</MenuItem>
                <MenuItem value="mp4">MP4</MenuItem>
                <MenuItem value="webm">WebM</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="开始时间 (秒)"
              type="number"
              value={options.startTime || ''}
              onChange={(e) => setOptions(prev => ({ ...prev, startTime: e.target.value }))}
              placeholder="可选"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="结束时间 (秒)"
              type="number"  
              value={options.endTime || ''}
              onChange={(e) => setOptions(prev => ({ ...prev, endTime: e.target.value }))}
              placeholder="可选"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              onClick={handleGetInfo}
              disabled={loading || !url}
              startIcon={<InfoIcon />}
            >
              {loading ? '获取中...' : '获取视频信息'}
            </Button>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              onClick={handleDownload}
              disabled={!url || downloading}
              startIcon={<CloudDownload />}
            >
              {downloading 
                ? (downloadStatus?.status === 'processing' ? '正在处理...' 
                   : downloadStatus?.status === 'downloading' ? '下载中...' 
                   : '启动中...') 
                : '开始下载'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {videoInfo && (
        <Card sx={{ mb: 3 }}>
          <Grid container>
            {videoInfo.thumbnail && (
              <Grid item xs={12} sm={4}>
                <CardMedia
                  component="img"
                  height="200"
                  image={videoInfo.thumbnail}
                  alt={videoInfo.title}
                />
              </Grid>
            )}
            <Grid item xs={12} sm={videoInfo.thumbnail ? 8 : 12}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {videoInfo.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  上传者: {videoInfo.uploader}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  时长: {formatDuration(videoInfo.duration)}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  观看次数: {videoInfo.view_count?.toLocaleString() || 'N/A'}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {videoInfo.formats.slice(0, 5).map((format, index) => (
                    <Chip
                      key={index}
                      label={`${format.resolution} (${format.ext})`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </CardContent>
            </Grid>
          </Grid>
        </Box>
      )}

      {downloading && (
        <Box sx={{ mt: 2 }}>
          <Paper sx={{ p: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs>
                <Typography variant="body2" gutterBottom>
                  下载进度
                </Typography>
              </Grid>
              <Grid item>
                <Button
                  size="small"
                  color="secondary"
                  onClick={handleCancel}
                  startIcon={<CancelIcon />}
                >
                  取消
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Box>
      )}

      {downloadStatus && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={downloadStatus.progress} 
            sx={{ mb: 1 }}
          />
          <Grid container spacing={2} justifyContent="space-between">
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                {downloadStatus.progress.toFixed(1)}%
              </Typography>
            </Grid>
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                {formatFileSize(downloadStatus.speed)}/s
              </Typography>
            </Grid>
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                剩余时间: {downloadStatus.eta} 秒
              </Typography>
            </Grid>
          </Grid>
          
          {downloadStatus.status === 'finished' && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Button
                variant="contained"
                color="success"
                onClick={handleDownloadFile}
                startIcon={<CloudDownload />}
              >
                下载文件
              </Button>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default VideoDownloader;