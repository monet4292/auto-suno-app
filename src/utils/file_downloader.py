"""
File Downloader Utility for Suno
Extracted from legacy_modules/suno_batch_download.py

Handles downloading audio files and thumbnails with progress tracking
"""
import os
import re
import time
import requests
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.utils.logger import logger


class SunoFileDownloader:
    """
    Handles downloading files from Suno (audio and thumbnails)

    Responsibilities:
    - Download audio files with progress tracking
    - Download thumbnail images
    - Handle filename sanitization and uniqueness
    - Proxy support for downloads
    """

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize file downloader

        Args:
            proxy_list: List of proxy URLs for requests
        """
        self.proxy_list = proxy_list or []

    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the proxy list"""
        if not self.proxy_list:
            return None
        proxy_url = self.proxy_list[len(self.proxy_list) % len(self.proxy_list)]
        return {'http': proxy_url, 'https': proxy_url}

    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize filename by removing invalid characters

        Args:
            name: Original filename

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = r'<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')

        # Remove control characters
        name = re.sub(r'[\x00-\x1f\x7f]', '', name)

        # Trim spaces and dots at end
        name = name.strip().rstrip('.')

        return name

    def ensure_unique_filename(self, directory: str, base_name: str,
                              extension: str = '.mp3') -> str:
        """
        Ensure filename is unique in directory

        Args:
            directory: Target directory
            base_name: Base filename (without extension)
            extension: File extension

        Returns:
            Unique filepath
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        filepath = directory / f"{base_name}{extension}"
        counter = 1

        while filepath.exists():
            filepath = directory / f"{base_name}_{counter}{extension}"
            counter += 1

        return str(filepath)

    def download_audio(self, clip_info: Dict[str, Any], directory: str,
                      append_uuid: bool = False) -> Optional[str]:
        """
        Download audio file from clip info

        Args:
            clip_info: Clip information dictionary
            directory: Download directory
            append_uuid: Whether to append UUID to filename

        Returns:
            Path to downloaded file or None if failed
        """
        title = clip_info.get('title', 'Untitled')
        clip_id = clip_info.get('id', 'unknown')
        audio_url = clip_info.get('audio_url')

        if not audio_url:
            logger.warning(f"No audio URL for: {title}")
            return None

        # Create filename
        safe_title = self.sanitize_filename(title)
        if append_uuid:
            base_name = f"{safe_title}__ID__{clip_id}"
        else:
            base_name = safe_title

        file_path = self.ensure_unique_filename(directory, base_name, '.mp3')

        try:
            proxies = self._get_random_proxy()
            response = requests.get(audio_url, proxies=proxies, stream=True, timeout=60)
            response.raise_for_status()

            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Log progress for large files
                    if total_size > 1024 * 1024:  # > 1MB
                        progress = (downloaded / total_size) * 100 if total_size else 0
                        logger.debug(f"Download progress: {progress:.1f}%")

            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            logger.info(f"✓ Downloaded: {Path(file_path).name} ({size_mb:.2f} MB)")

            return file_path

        except Exception as e:
            logger.error(f"❌ Failed to download {title}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None

    def download_thumbnail(self, clip_info: Dict[str, Any], directory: str) -> Optional[str]:
        """
        Download thumbnail/cover art

        Args:
            clip_info: Clip information dictionary
            directory: Download directory

        Returns:
            Path to downloaded thumbnail or None if failed
        """
        image_url = clip_info.get('image_url')
        if not image_url:
            return None

        clip_id = clip_info.get('id', 'unknown')
        filename = f"{clip_id}_cover.jpg"
        file_path = Path(directory) / filename

        try:
            proxies = self._get_random_proxy()
            response = requests.get(image_url, proxies=proxies, timeout=30)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"✓ Downloaded thumbnail: {filename}")
            return str(file_path)

        except Exception as e:
            logger.warning(f"⚠️ Failed to download thumbnail: {e}")
            return None

    def download_batch(self, clips: List[Dict[str, Any]], directory: str,
                      with_thumbnails: bool = False, append_uuid: bool = False,
                      delay_between_downloads: float = 2.0) -> Dict[str, Any]:
        """
        Download multiple clips in batch

        Args:
            clips: List of clip info dictionaries
            directory: Download directory
            with_thumbnails: Whether to download thumbnails
            append_uuid: Whether to append UUID to filenames
            delay_between_downloads: Delay between downloads in seconds

        Returns:
            Statistics dictionary
        """
        logger.info(f"Starting batch download of {len(clips)} clips")

        # Create directory
        Path(directory).mkdir(parents=True, exist_ok=True)

        stats = {
            'total': len(clips),
            'successful': 0,
            'failed': 0,
            'downloaded_files': []
        }

        for idx, clip in enumerate(clips, 1):
            title = clip.get('title', 'Unknown')
            logger.info(f"[{idx}/{len(clips)}] Downloading: {title}")

            # Download audio
            audio_path = self.download_audio(clip, directory, append_uuid)

            if audio_path:
                stats['successful'] += 1
                stats['downloaded_files'].append({
                    'title': title,
                    'audio_path': audio_path,
                    'thumbnail_path': None
                })

                # Download thumbnail if requested
                if with_thumbnails:
                    thumbnail_path = self.download_thumbnail(clip, directory)
                    if thumbnail_path:
                        stats['downloaded_files'][-1]['thumbnail_path'] = thumbnail_path

            else:
                stats['failed'] += 1

            # Delay between downloads
            if idx < len(clips):
                time.sleep(delay_between_downloads)

        logger.info(f"Batch download completed: {stats['successful']} successful, {stats['failed']} failed")
        return stats

    def validate_download(self, file_path: str, expected_size: Optional[int] = None) -> bool:
        """
        Validate downloaded file

        Args:
            file_path: Path to downloaded file
            expected_size: Expected file size in bytes (optional)

        Returns:
            True if file is valid, False otherwise
        """
        if not os.path.exists(file_path):
            return False

        file_size = os.path.getsize(file_path)

        # Check minimum size (empty files are invalid)
        if file_size == 0:
            return False

        # Check expected size if provided
        if expected_size and abs(file_size - expected_size) > 1024:  # Allow 1KB tolerance
            logger.warning(f"File size mismatch: expected {expected_size}, got {file_size}")
            return False

        return True