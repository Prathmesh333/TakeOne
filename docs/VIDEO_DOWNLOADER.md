# Video Downloader - URL Support Documentation

## Overview

The CineSearch-AI pipeline now supports processing videos directly from URLs. You can provide YouTube links, Google Drive links, direct video URLs, or links from other video platforms, and the system will automatically download and process them.

## Supported Platforms

### Fully Supported
- **YouTube** (youtube.com, youtu.be)
- **Google Drive** (drive.google.com)
- **Direct Video Links** (.mp4, .mov, .avi, .mkv, .webm, .flv, .wmv, .m4v)

### Supported via yt-dlp
- **Vimeo** (vimeo.com)
- **Dailymotion** (dailymotion.com)
- **Twitter/X** (twitter.com, x.com)
- **Facebook** (facebook.com)
- **Instagram** (instagram.com)
- **TikTok** (tiktok.com)
- **And 1000+ other sites** supported by yt-dlp

## Installation

### Required Packages

```bash
pip install yt-dlp gdown requests
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# YouTube video
python -m ingestion.pipeline "https://www.youtube.com/watch?v=VIDEO_ID"

# YouTube short URL
python -m ingestion.pipeline "https://youtu.be/VIDEO_ID"

# Google Drive
python -m ingestion.pipeline "https://drive.google.com/file/d/FILE_ID/view"

# Direct video link
python -m ingestion.pipeline "https://example.com/video.mp4"

# Vimeo
python -m ingestion.pipeline "https://vimeo.com/VIDEO_ID"

# Keep downloaded file (don't cleanup)
python -m ingestion.pipeline "https://youtube.com/watch?v=ID" --no-cleanup
```

### Python API

```python
from ingestion.pipeline import TakeOnePipeline

pipeline = TakeOnePipeline()

# Process from URL
results = pipeline.process_video(
    video_path="https://www.youtube.com/watch?v=VIDEO_ID",
    cleanup_download=True  # Delete after processing (default)
)

# Check if it was downloaded
if results['downloaded_from_url']:
    print(f"Downloaded from: {results['original_url']}")
    print(f"Video title: {results['video_id']}")
```

### Standalone Downloader

```python
from ingestion.video_downloader import VideoDownloader

# Initialize downloader
downloader = VideoDownloader(download_dir="./downloads")

# Download video
file_path, metadata = downloader.download(
    "https://www.youtube.com/watch?v=VIDEO_ID"
)

print(f"Downloaded to: {file_path}")
print(f"Title: {metadata['title']}")
print(f"Duration: {metadata['duration']}s")

# Cleanup when done
downloader.cleanup(file_path)
```

## Features

### Automatic Platform Detection

The downloader automatically detects the platform from the URL:

```python
from ingestion.video_downloader import VideoDownloader

downloader = VideoDownloader()

# Automatically detects YouTube
downloader.download("https://youtube.com/watch?v=ID")

# Automatically detects Google Drive
downloader.download("https://drive.google.com/file/d/ID/view")

# Automatically detects direct link
downloader.download("https://example.com/video.mp4")
```

### Metadata Extraction

Downloaded videos include metadata:

```python
file_path, metadata = downloader.download(url)

# YouTube metadata
{
    'title': 'Video Title',
    'duration': 120,  # seconds
    'uploader': 'Channel Name',
    'upload_date': '20240128',
    'description': 'Video description...',
    'platform': 'youtube',
    'url': 'original_url'
}

# Google Drive metadata
{
    'title': 'filename',
    'platform': 'google_drive',
    'file_id': 'FILE_ID',
    'url': 'original_url'
}

# Direct link metadata
{
    'title': 'video.mp4',
    'platform': 'direct',
    'url': 'original_url',
    'size_bytes': 10485760
}
```

### Automatic Cleanup

By default, downloaded files are automatically deleted after processing:

```python
# Cleanup enabled (default)
results = pipeline.process_video(
    "https://youtube.com/watch?v=ID",
    cleanup_download=True
)

# Keep downloaded file
results = pipeline.process_video(
    "https://youtube.com/watch?v=ID",
    cleanup_download=False
)
```

### Custom Download Directory

```python
# Specify download directory
downloader = VideoDownloader(download_dir="./my_downloads")

# Or use pipeline output directory
pipeline = TakeOnePipeline(output_dir="./output")
# Downloads go to ./output/downloads/
```

## Platform-Specific Notes

### YouTube

**Requirements**: `yt-dlp`

**Features**:
- Automatic quality selection (prefers MP4)
- Metadata extraction (title, uploader, duration, etc.)
- Playlist support (downloads first video)

**Example URLs**:
```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/watch?v=VIDEO_ID&t=30s
```

### Google Drive

**Requirements**: `gdown` (recommended) or `requests` (fallback)

**Features**:
- Direct file download
- Large file support (>100MB)
- Automatic virus scan warning handling

**Example URLs**:
```
https://drive.google.com/file/d/FILE_ID/view
https://drive.google.com/open?id=FILE_ID
https://drive.google.com/uc?id=FILE_ID
```

**Note**: File must be publicly accessible or shared with "Anyone with the link"

### Direct Video Links

**Requirements**: `requests`

**Features**:
- Simple HTTP download
- Progress tracking
- Resume support (if server supports)

**Supported Extensions**:
- .mp4, .mov, .avi, .mkv, .webm
- .flv, .wmv, .m4v

**Example URLs**:
```
https://example.com/video.mp4
https://cdn.example.com/media/video.mov
https://storage.example.com/videos/clip.avi
```

### Other Platforms (via yt-dlp)

**Requirements**: `yt-dlp`

**Supported Platforms**: 1000+ sites including:
- Vimeo
- Dailymotion
- Twitter/X
- Facebook
- Instagram
- TikTok
- Twitch
- Reddit
- And many more

**Example**:
```python
# Vimeo
downloader.download("https://vimeo.com/123456789")

# Twitter
downloader.download("https://twitter.com/user/status/123456789")

# Instagram
downloader.download("https://www.instagram.com/p/ABC123/")
```

## Error Handling

### Common Errors

**"yt-dlp is required"**
```bash
pip install yt-dlp
```

**"gdown is required"** (for Google Drive)
```bash
pip install gdown
```

**"Could not extract Google Drive file ID"**
- Check URL format
- Ensure file is publicly accessible
- Try different URL format

**"Download failed: HTTP 403"**
- Video may be private or restricted
- Check if video is available in your region
- Try different quality/format

### Handling Errors in Code

```python
from ingestion.video_downloader import VideoDownloader

downloader = VideoDownloader()

try:
    file_path, metadata = downloader.download(url)
    print(f"Success: {file_path}")
except ValueError as e:
    print(f"Invalid URL: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
except Exception as e:
    print(f"Download failed: {e}")
```

## Configuration

### Download Quality

For YouTube and other platforms, quality is automatically selected:

```python
# Default: best quality MP4
# Falls back to best available format if MP4 not available
```

To customize quality, modify `ydl_opts` in `video_downloader.py`:

```python
ydl_opts = {
    'format': 'best[height<=720]',  # Max 720p
    # or
    'format': 'worst',  # Lowest quality (faster download)
    # or
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]',  # Best video+audio
}
```

### Timeout Settings

```python
# For direct downloads, set timeout
response = requests.get(url, stream=True, timeout=30)
```

### Retry Logic

```python
# Implement retry for failed downloads
max_retries = 3
for attempt in range(max_retries):
    try:
        file_path, metadata = downloader.download(url)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
        raise
```

## Performance

### Download Speeds

Typical download speeds:
- **YouTube**: 5-20 MB/s (depends on video quality)
- **Google Drive**: 10-50 MB/s (depends on file size)
- **Direct Links**: Varies by server

### Processing Time

For a 2-minute 1080p video:
- Download: 10-30 seconds
- Processing: 110 seconds (with YOLO)
- Total: ~2-3 minutes

### Storage Requirements

Downloaded files are stored temporarily:
- Location: `output_dir/downloads/`
- Cleanup: Automatic (unless disabled)
- Space needed: ~2x video file size (original + processed clips)

## Best Practices

### 1. Use Cleanup

Always enable cleanup for production:

```python
results = pipeline.process_video(url, cleanup_download=True)
```

### 2. Validate URLs

Check if input is URL before processing:

```python
from ingestion.video_downloader import VideoDownloader

downloader = VideoDownloader()

if downloader.is_url(input_path):
    # Process as URL
    results = pipeline.process_video(input_path)
else:
    # Process as local file
    results = pipeline.process_video(input_path)
```

### 3. Handle Errors Gracefully

```python
try:
    results = pipeline.process_video(url)
except ValueError as e:
    print(f"Invalid URL: {e}")
except ImportError as e:
    print(f"Install required package: {e}")
except Exception as e:
    print(f"Processing failed: {e}")
```

### 4. Monitor Storage

```python
import shutil

# Check available space
total, used, free = shutil.disk_usage("/")
print(f"Free space: {free // (2**30)} GB")

# Cleanup old downloads
downloader.cleanup(old_file_path)
```

### 5. Use Appropriate Quality

For faster processing, use lower quality:
- 720p is sufficient for most analysis
- 1080p for high-quality requirements
- 4K only if necessary (much slower)

## Troubleshooting

### Issue: "Video unavailable"

**Causes**:
- Video is private
- Video is region-restricted
- Video was deleted

**Solutions**:
- Check video accessibility in browser
- Try different URL format
- Use VPN if region-restricted

### Issue: "Download too slow"

**Solutions**:
- Check internet connection
- Try different time of day
- Use lower quality setting
- Use direct link if available

### Issue: "Out of disk space"

**Solutions**:
- Enable cleanup: `cleanup_download=True`
- Use smaller videos
- Clear download directory manually
- Increase available storage

### Issue: "Google Drive quota exceeded"

**Causes**:
- Too many downloads from same file
- File owner's quota exceeded

**Solutions**:
- Wait 24 hours
- Request file owner to increase quota
- Use alternative hosting

## Examples

### Example 1: Process YouTube Video

```python
from ingestion.pipeline import TakeOnePipeline

pipeline = TakeOnePipeline()

results = pipeline.process_video(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    use_yolo=True,
    yolo_scene_detection=True,
    cleanup_download=True
)

print(f"Processed: {results['video_id']}")
print(f"Scenes: {results['stages']['scene_detection']['optimized_scenes']}")
```

### Example 2: Batch Process URLs

```python
urls = [
    "https://youtube.com/watch?v=ID1",
    "https://drive.google.com/file/d/ID2/view",
    "https://example.com/video.mp4"
]

for url in urls:
    try:
        results = pipeline.process_video(url)
        print(f"SUCCESS: {results['video_id']}")
    except Exception as e:
        print(f"FAILED: {url} - {e}")
```

### Example 3: Download Only

```python
from ingestion.video_downloader import download_video

# Download without processing
file_path, metadata = download_video(
    "https://youtube.com/watch?v=ID",
    output_dir="./downloads"
)

print(f"Downloaded: {file_path}")
print(f"Title: {metadata['title']}")
print(f"Duration: {metadata['duration']}s")
```

## API Reference

### VideoDownloader Class

```python
class VideoDownloader:
    def __init__(self, download_dir: str = None)
    def download(self, url: str, output_filename: str = None) -> Tuple[str, Dict]
    def is_url(self, path: str) -> bool
    def cleanup(self, file_path: str)
```

### Pipeline Integration

```python
pipeline.process_video(
    video_path: str,  # Can be URL or local path
    cleanup_download: bool = True,  # Auto-cleanup downloaded files
    **other_args
)
```

## Conclusion

The video downloader feature enables seamless processing of videos from various online platforms. Simply provide a URL instead of a file path, and the system handles the rest automatically.

For questions or issues, refer to the troubleshooting section or check the yt-dlp documentation for platform-specific details.
