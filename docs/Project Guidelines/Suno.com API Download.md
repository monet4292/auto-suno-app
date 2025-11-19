📚 Suno.com API Download Documentation
1. API Overview
Base Configuration
# Base URL
BASE_URL = "https://studio-api.prod.suno.com/api"

# Authentication
Authorization: Bearer {session_token}
Content-Type: application/json

# Session Token Source
Cookie: __session={jwt_token}

2. Download Methods Available
Method 1: Download from User's Library (/me)
# Fetch from user's personal library
def fetch_my_clips(self) -> List[Dict]:
    endpoint = "/feed/v2"
    params = {'page': 0}
    
    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    data = response.json()
    return data.get('clips', [])

Method 2: Download from Create Page Context
# Fetch clips accessible from /create page
def fetch_create_clips(self) -> List[Dict]:
    endpoint = "/feed/v2"
    params = {'page': 0}
    
    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    data = response.json()
    return data.get('clips', [])

3. Download Workflow
3.1 Complete Download Process

def batch_download_paginated(
    self,
    account_name: str,
    session_token: str,
    output_dir: Path,
    progress_callback: Optional[callable] = None
) -> Dict[str, int]:
    """
    Complete download workflow with pagination
    """
    # 1. Initialize
    history = self.get_history(account_name)
    stats = {'success': 0, 'failed': 0, 'skipped': 0}
    
    # 2. Update API client
    self.api_client.update_session_token(session_token)
    
    # 3. Pagination loop
    current_page = 0
    while True:
        # 3.1 Fetch clips page
        clips, last_page, has_more = self.api_client.fetch_clips_page(current_page)
        
        if not clips:
            break
        
        # 3.2 Process each clip
        for clip in clips:
            # 3.2.1 Check if already downloaded
            if history.is_downloaded(clip.id):
                stats['skipped'] += 1
                continue
            
            # 3.2.2 Download audio file
            audio_success = self.file_downloader.download_mp3_file(
                clip.audio_url,
                output_dir / f"{clip.title}__ID__{clip.id[:8]}.mp3",
                progress_callback=lambda pct: progress_callback(
                    f"Downloading {clip.title}", pct
                ) if progress_callback else None
            )
            
            # 3.2.3 Download image file
            image_success = self.file_downloader.download_image_file(
                clip.image_url,
                output_dir / f"{clip.title}__ID__{clip.id[:8]}.jpg",
                progress_callback=lambda pct: progress_callback(
                    f"Downloading image for {clip.title}", pct
                ) if progress_callback else None
            ) if clip.image_url else True
            
            # 3.2.4 Embed metadata
            if audio_success and image_success:
                metadata_success = self.metadata_handler.embed_id3_tags(
                    output_dir / f"{clip.title}__ID__{clip.id[:8]}.mp3",
                    clip
                )
                
                if metadata_success:
                    history.add_download(clip.id)
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
            else:
                stats['failed'] += 1
        
        # 3.3 Check for more pages
        if not has_more:
            break
        
        current_page += 1
    
    # 4. Save history
    self.save_histories()
    
    return stats

3.2 File Download Implementation
# File downloader with progress tracking
class SunoFileDownloader:
    def download_mp3_file(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """Download MP3 file with progress tracking"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress callback
                        if progress_callback and total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            progress_callback(percent)
            
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

3.3 Metadata Embedding
# ID3 metadata handler
class SunoMetadataHandler:
    def embed_id3_tags(
        self,
        audio_path: Path,
        clip: Dict[str, Any]
    ) -> bool:
        """Embed ID3 tags into MP3 file"""
        try:
            from mutagen.id3 import ID3, ID3v2SaveOptions
            
            audio = ID3(audio_path)
            
            # Basic metadata
            audio['title'] = clip.get('title', 'Unknown Title')
            audio['artist'] = clip.get('metadata', {}).get('display_name', 'Unknown Artist')
            audio['album'] = "Suno Generated"
            
            # Add artwork if available
            if clip.get('image_url'):
                image_path = audio_path.with_suffix('.jpg')
                if self.download_image_file(clip['image_url'], image_path):
                    with open(image_path, 'rb') as image_file:
                        audio['artwork'] = image_file.read()
            
            # Custom metadata
            audio['comment'] = f"Generated with Suno.com"
            audio['website'] = "https://suno.com"
            
            # Save with ID3v2.3
            audio.save(v2_version=ID3v2SaveOptions.V3)
            return True
            
        except Exception as e:
            logger.error(f"Metadata embedding failed: {e}")
            return False

4. Rate Limiting
Rate Limits per Endpoint
Endpoint	Rate Limit	Time Window
/billing/info	10 req/min	1 minute
/feed/v2	30 req/min	1 minute
/clips/profile/{username}	60 req/min	1 minute
/generate	5 req/min	1 minute
/clip/{clip_id}	100 req/min	1 minute

Rate Limit Handling
def _handle_rate_limit(self, response: requests.Response) -> bool:
    """Handle rate limiting from API responses"""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        logger.warning(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        return True
    return False

# Usage in download loop
for attempt in range(MAX_RETRIES):
    response = requests.get(url, headers=headers)
    
    if self._handle_rate_limit(response):
        continue  # Retry after waiting
    
    response.raise_for_status()
    break

5. Error Handling
Common Error Codes
Code	Meaning	Handling
401	Unauthorized	Refresh session token
402	Payment Required	Check credits
403	Forbidden	Check permissions
404	Not Found	Invalid clip ID
429	Too Many Requests	Implement backoff
500	Server Error	Retry with exponential backoff

Error Handling Implementation
def download_with_retry(self, clip: Dict, max_retries: int = 3) -> bool:
    """Download with retry logic"""
    for attempt in range(max_retries):
        try:
            success = self.download_clip(clip)
            if success:
                return True
                
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit - wait longer
                wait_time = (2 ** attempt) * 10
                logger.warning(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif e.response.status_code >= 500:
                # Server error - retry with backoff
                wait_time = (2 ** attempt) * 5
                logger.warning(f"Server error, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                # Client error - don't retry
                logger.error(f"Client error: {e}")
                return False
                
    logger.error(f"Failed after {max_retries} attempts")
    return False

6. Progress Tracking
Progress Callback Implementation
def progress_callback(message: str, percent: int) -> None:
    """Progress callback for UI updates"""
    # Send to UI via various methods:
    # 1. Direct callback (for same-process UI)
    if hasattr(self, 'progress_callback'):
        self.progress_callback(message, percent)
    
    # 2. WebSocket (for separate process UI)
    if hasattr(self, 'websocket'):
        self.websocket.emit('download_progress', {
            'message': message,
            'percent': percent
        })
    
    # 3. File-based (for CLI)
    with open('progress.log', 'a') as f:
        f.write(f"{datetime.now()}: {message} - {percent}%\n")

Progress Tracking in UI
# In UI component
def update_progress(self, message: str, percent: int) -> None:
    """Update progress bar in UI"""
    self.progress_label.configure(text=message)
    self.progress_bar.set(percent / 100.0)
    
    # Force UI update
    self.update_idletasks()

7. File Organization
Directory Structure
downloads/
├── account_name/
│   ├── Song Title__ID__abc12345.mp3
│   ├── Song Title__ID__abc12345.jpg
│   └── metadata/
│       ├── Song Title__ID__abc12345.json
│       └── thumbnails/
└── temp/
    └── downloads/
        └── partial_*.mp3.temp

File Naming Convention
def generate_filename(clip: Dict) -> str:
    """Generate safe filename for clip"""
    title = clip.get('title', 'Unknown Title')
    clip_id = clip.get('id', 'unknown')
    
    # Clean title for filesystem
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    safe_title = safe_title[:100]  # Limit length
    
    # Extract first 8 chars of ID
    short_id = clip_id[:8] if len(clip_id) >= 8 else clip_id
    
    return f"{safe_title}__ID__{short_id}"

This comprehensive API documentation shows how to download songs through the Suno.com API with proper authentication, rate limiting, error handling, and progress tracking. The implementation includes both direct API calls and file download with metadata embedding.