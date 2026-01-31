"""
Video Downloader - Downloads videos from various platforms
Supports YouTube, Google Drive, direct links, and other video platforms
"""

import os
import re
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse, parse_qs
import tempfile

logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Downloads videos from various platforms.
    
    Supported platforms:
    - YouTube (youtube.com, youtu.be)
    - Google Drive (drive.google.com)
    - Direct video links (.mp4, .mov, .avi, .mkv, .webm)
    - Vimeo (vimeo.com)
    - Dailymotion (dailymotion.com)
    - Other platforms supported by yt-dlp
    """
    
    def __init__(self, download_dir: str = None):
        """
        Initialize video downloader.
        
        Args:
            download_dir: Directory to save downloaded videos (default: temp directory)
        """
        if download_dir:
            self.download_dir = Path(download_dir)
            self.download_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.download_dir = Path(tempfile.gettempdir()) / "cinesearch_downloads"
            self.download_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Video downloader initialized. Download directory: {self.download_dir}")
    
    def download(self, url: str, output_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Download video from URL.
        
        Args:
            url: Video URL (YouTube, Google Drive, direct link, etc.)
            output_filename: Optional custom filename
            
        Returns:
            Tuple of (file_path, metadata_dict)
            
        Raises:
            ValueError: If URL is invalid or unsupported
            Exception: If download fails
        """
        logger.info(f"Processing URL: {url}")
        
        # Detect platform
        platform = self._detect_platform(url)
        logger.info(f"Detected platform: {platform}")
        
        # Download based on platform
        if platform == "youtube":
            return self._download_youtube(url, output_filename)
        elif platform == "google_drive":
            return self._download_google_drive(url, output_filename)
        elif platform == "direct":
            return self._download_direct(url, output_filename)
        elif platform in ["vimeo", "dailymotion", "other"]:
            return self._download_with_ytdlp(url, output_filename)
        else:
            raise ValueError(f"Unsupported platform or invalid URL: {url}")
    
    def _detect_platform(self, url: str) -> str:
        """Detect video platform from URL."""
        url_lower = url.lower()
        
        # YouTube
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        
        # Google Drive
        if "drive.google.com" in url_lower:
            return "google_drive"
        
        # Vimeo
        if "vimeo.com" in url_lower:
            return "vimeo"
        
        # Dailymotion
        if "dailymotion.com" in url_lower:
            return "dailymotion"
        
        # Direct video link
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        if any(ext in url_lower for ext in video_extensions):
            return "direct"
        
        # Try with yt-dlp for other platforms
        return "other"
    
    def _download_youtube(self, url: str, output_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """Download video from YouTube using yt-dlp with enhanced options."""
        try:
            import yt_dlp
        except ImportError:
            raise ImportError(
                "yt-dlp is required for YouTube downloads. "
                "Install with: pip install yt-dlp"
            )
        
        # Configure yt-dlp options
        if output_filename:
            output_path = str(self.download_dir / output_filename)
        else:
            output_path = str(self.download_dir / "%(title)s.%(ext)s")
        
        # Enhanced options to avoid 403 errors
        ydl_opts = {
            'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',  # Prefer MP4, max 1080p
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            # Add user agent to avoid blocks
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Use multiple extractors for better compatibility
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']  # Skip problematic formats
                }
            },
            # Add headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # Retry options
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
        }
        
        logger.info("Downloading from YouTube with enhanced compatibility...")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info
                info = ydl.extract_info(url, download=True)
                
                # Get actual filename
                if output_filename:
                    file_path = output_path
                else:
                    file_path = ydl.prepare_filename(info)
                
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'description': info.get('description', ''),
                    'platform': 'youtube',
                    'url': url
                }
                
                logger.info(f"Download complete: {file_path}")
                return file_path, metadata
                
        except Exception as e:
            logger.error(f"YouTube download failed: {e}")
            logger.info("Tip: Make sure yt-dlp is up to date: pip install -U yt-dlp")
            raise
    
    def _download_google_drive(self, url: str, output_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """Download video from Google Drive."""
        # Extract file ID from URL
        file_id = self._extract_gdrive_id(url)
        if not file_id:
            raise ValueError("Could not extract Google Drive file ID from URL")
        
        logger.info(f"Google Drive file ID: {file_id}")
        
        # Use gdown library if available, otherwise use direct download
        try:
            import gdown
            
            if output_filename:
                output_path = str(self.download_dir / output_filename)
            else:
                output_path = str(self.download_dir / f"gdrive_{file_id}.mp4")
            
            logger.info("Downloading from Google Drive...")
            gdown.download(id=file_id, output=output_path, quiet=False)
            
            metadata = {
                'title': output_filename or f"gdrive_{file_id}",
                'platform': 'google_drive',
                'file_id': file_id,
                'url': url
            }
            
            logger.info(f"Download complete: {output_path}")
            return output_path, metadata
            
        except ImportError:
            # Fallback to direct download
            logger.warning("gdown not installed, using direct download method")
            return self._download_gdrive_direct(file_id, output_filename, url)
    
    def _extract_gdrive_id(self, url: str) -> Optional[str]:
        """Extract file ID from Google Drive URL."""
        # Pattern 1: /file/d/{id}/
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        
        # Pattern 2: id={id}
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        
        # Pattern 3: /open?id={id}
        match = re.search(r'/open\?id=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def _download_gdrive_direct(self, file_id: str, output_filename: Optional[str], url: str) -> Tuple[str, Dict]:
        """Download from Google Drive using direct method."""
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        if output_filename:
            output_path = self.download_dir / output_filename
        else:
            output_path = self.download_dir / f"gdrive_{file_id}.mp4"
        
        logger.info("Downloading from Google Drive (direct method)...")
        
        session = requests.Session()
        response = session.get(download_url, stream=True)
        
        # Handle large file confirmation
        if 'download_warning' in response.text or 'virus scan warning' in response.text:
            # Get confirmation token
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    download_url = f"{download_url}&confirm={value}"
                    response = session.get(download_url, stream=True)
                    break
        
        # Download file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        metadata = {
            'title': output_filename or f"gdrive_{file_id}",
            'platform': 'google_drive',
            'file_id': file_id,
            'url': url
        }
        
        logger.info(f"Download complete: {output_path}")
        return str(output_path), metadata
    
    def _download_direct(self, url: str, output_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """Download video from direct URL."""
        if not output_filename:
            # Extract filename from URL
            parsed = urlparse(url)
            output_filename = Path(parsed.path).name
            if not output_filename:
                output_filename = "video.mp4"
        
        output_path = self.download_dir / output_filename
        
        logger.info(f"Downloading from direct URL...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                logger.info(f"Download progress: {progress:.1f}%")
        
        metadata = {
            'title': output_filename,
            'platform': 'direct',
            'url': url,
            'size_bytes': total_size
        }
        
        logger.info(f"Download complete: {output_path}")
        return str(output_path), metadata
    
    def _download_with_ytdlp(self, url: str, output_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """Download video using yt-dlp (supports many platforms)."""
        try:
            import yt_dlp
        except ImportError:
            raise ImportError(
                "yt-dlp is required for this platform. "
                "Install with: pip install yt-dlp"
            )
        
        if output_filename:
            output_path = str(self.download_dir / output_filename)
        else:
            output_path = str(self.download_dir / "%(title)s.%(ext)s")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
        }
        
        logger.info(f"Downloading with yt-dlp...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if output_filename:
                file_path = output_path
            else:
                file_path = ydl.prepare_filename(info)
            
            metadata = {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'platform': info.get('extractor', 'unknown'),
                'url': url
            }
            
            logger.info(f"Download complete: {file_path}")
            return file_path, metadata
    
    def is_url(self, path: str) -> bool:
        """Check if string is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def cleanup(self, file_path: str):
        """Delete downloaded file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Could not cleanup {file_path}: {e}")


def download_video(url: str, output_dir: Optional[str] = None) -> Tuple[str, Dict]:
    """
    Convenience function to download a video.
    
    Args:
        url: Video URL
        output_dir: Optional output directory
        
    Returns:
        Tuple of (file_path, metadata)
    """
    downloader = VideoDownloader(download_dir=output_dir)
    return downloader.download(url)


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"Downloading: {url}")
        
        try:
            file_path, metadata = download_video(url, output_dir)
            print(f"\nDownload successful!")
            print(f"File: {file_path}")
            print(f"Metadata: {metadata}")
        except Exception as e:
            print(f"\nDownload failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Usage: python video_downloader.py <url> [output_dir]")
        print("\nSupported platforms:")
        print("  - YouTube (youtube.com, youtu.be)")
        print("  - Google Drive (drive.google.com)")
        print("  - Direct video links (.mp4, .mov, etc.)")
        print("  - Vimeo, Dailymotion, and others via yt-dlp")
