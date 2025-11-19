"""
Download Manager - Manages song download operations
"""
import os
import time
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from config.settings import HISTORY_FILE, DOWNLOADS_DIR
from src.models import DownloadHistory, SongClip, DownloadTask
from src.utils import load_json, save_json, logger
from src.core.suno_api_client import SunoApiClient
from src.utils.file_downloader import SunoFileDownloader
from src.utils.metadata_handler import SunoMetadataHandler


class DownloadManager:
    """Manages song download operations"""
    
    def __init__(self):
        self.histories: Dict[str, DownloadHistory] = {}
        self.api_client = SunoApiClient()
        self.file_downloader = SunoFileDownloader()
        self.metadata_handler = SunoMetadataHandler()
        self.load_histories()
    
    def load_histories(self) -> None:
        """Load download history from file"""
        data = load_json(HISTORY_FILE, {})
        self.histories = {}
        for account, hist_data in data.items():
            # Add account_name to data
            hist_data['account_name'] = account
            self.histories[account] = DownloadHistory.from_dict(hist_data)
        logger.info(f"Loaded download histories for {len(self.histories)} accounts")
    
    def save_histories(self) -> bool:
        """Save download history to file"""
        data = {}
        for account, history in self.histories.items():
            hist_dict = history.to_dict()
            # Remove account_name from dict since it's the key
            hist_dict.pop('account_name', None)
            data[account] = hist_dict
        
        if save_json(HISTORY_FILE, data):
            logger.info("Download histories saved")
            return True
        return False
    
    def get_history(self, account_name: str) -> DownloadHistory:
        """Get download history for account"""
        if account_name not in self.histories:
            self.histories[account_name] = DownloadHistory(account_name=account_name)
        return self.histories[account_name]
    
    def clear_history(self, account_name: str) -> bool:
        """Clear download history for account"""
        if account_name in self.histories:
            self.histories[account_name].clear()
            self.save_histories()
            logger.info(f"Cleared download history for: {account_name}")
            return True
        return False
    
    def fetch_clips(self, session_token: str, profile_name: str = None, use_my_songs: bool = False, use_create_page: bool = False) -> List[SongClip]:
        """Fetch clips from profile, /me, or /create endpoint"""
        try:
            # Update API client with session token
            self.api_client.update_session_token(session_token)
            
            if use_create_page:
                # Fetch from /create context (paginated)
                api_clips, last_page, has_more = self.api_client.fetch_create_clips_paginated(start_page=0, max_pages=None)
                logger.info(f"Fetched {len(api_clips)} clips from /create (last_page={last_page}, has_more={has_more})")
            elif use_my_songs:
                # Fetch from /me (legacy)
                api_clips = self.api_client.fetch_my_clips()
                logger.info(f"Fetched {len(api_clips)} clips from /me")
            else:
                # Fetch from profile (get first page only for compatibility)
                clips, _, _ = self.api_client.fetch_profile_clips(profile_name, max_pages=1)
                api_clips = clips
                logger.info(f"Fetched {len(api_clips)} clips from {profile_name}")
            
            clips = [SongClip.from_api_response(clip) for clip in api_clips]
            return clips
            
        except Exception as e:
            logger.error(f"Failed to fetch clips: {e}")
            return []
    
    def get_user_info(self, session_token: str) -> dict:
        """Get current user information"""
        try:
            self.api_client.update_session_token(session_token)
            user_info = self.api_client.get_current_user_info()
            return user_info or {}
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {}
    
    def get_new_clips(self, account_name: str, all_clips: List[SongClip]) -> List[SongClip]:
        """Filter clips that haven't been downloaded yet"""
        history = self.get_history(account_name)
        new_clips = [
            clip for clip in all_clips
            if not history.is_downloaded(clip.id)
        ]
        logger.info(f"Found {len(new_clips)} new clips for {account_name}")
        return new_clips
    
    def download_clip(
        self,
        session_token: str,
        clip: SongClip,
        output_dir: Path,
        with_thumbnail: bool = True,
        append_uuid: bool = True,
        progress_callback = None
    ) -> bool:
        """Download a single clip"""
        try:
            # Convert SongClip to dict format expected by downloader
            clip_data = {
                'id': clip.id,
                'title': clip.title,
                'audio_url': clip.audio_url,
                'image_url': clip.image_url,
                'display_name': getattr(clip, 'display_name', 'Unknown Artist'),
                'metadata': {
                    'tags': clip.tags if clip.tags else ''
                }
            }
            
            # Download audio
            if progress_callback:
                progress_callback(f"Downloading: {clip.title}", 30)
            
            audio_path = self.file_downloader.download_audio(clip_data, str(output_dir), append_uuid)
            
            if not audio_path:
                logger.error(f"Failed to download audio: {clip.title}")
                return False
            
            # Download thumbnail and embed metadata
            if with_thumbnail:
                if progress_callback:
                    progress_callback(f"Embedding metadata: {clip.title}", 70)
                
                thumbnail_path = self.file_downloader.download_thumbnail(clip_data, str(output_dir))
                self.metadata_handler.embed_metadata(audio_path, clip_data, thumbnail_path)
                
                # Remove thumbnail file
                if thumbnail_path:
                    try:
                        os.remove(thumbnail_path)
                    except Exception:
                        pass
            
            if progress_callback:
                progress_callback(f"Completed: {clip.title}", 100)
            
            logger.info(f"Downloaded: {clip.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download clip {clip.title}: {e}")
            return False
    
    def batch_download(
        self,
        account_name: str,
        session_token: str,
        clips: List[SongClip],
        output_dir: Path,
        with_thumbnail: bool = True,
        append_uuid: bool = True,
        progress_callback = None,
        delay: int = 2
    ) -> Dict[str, int]:
        """Batch download multiple clips"""
        
        history = self.get_history(account_name)
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        total = len(clips)
        
        for idx, clip in enumerate(clips, 1):
            if progress_callback:
                progress_callback(f"Processing {idx}/{total}: {clip.title}", (idx-1) * 100 // total)
            
            # Skip if already downloaded
            if history.is_downloaded(clip.id):
                stats['skipped'] += 1
                continue
            
            # Download clip
            success = self.download_clip(
                session_token, clip, output_dir,
                with_thumbnail, append_uuid, None
            )
            
            if success:
                history.add_download(clip.id)
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            # Delay between downloads
            if idx < total:
                time.sleep(delay)
        
        # Save history
        self.save_histories()
        
        logger.info(f"Batch download completed: {stats}")
        return stats
    
    def batch_download_paginated(
        self,
        account_name: str,
        session_token: str,
        output_dir: Path,
        profile_name: str = None,
        use_create_page: bool = False,
        start_page: int = 0,
        max_pages: Optional[int] = None,
        max_clips: Optional[int] = None,
        with_thumbnail: bool = True,
        append_uuid: bool = True,
        progress_callback = None,
        delay: int = 2
    ) -> Dict[str, int]:
        """
        Batch download with pagination - fetches and downloads page-by-page to save memory.
        
        Args:
            account_name: Account name for history tracking
            session_token: JWT session token
            output_dir: Output directory for downloads
            profile_name: Profile name (if downloading from profile)
            use_create_page: If True, fetch from /create feed; if False, fetch from profile
            start_page: Starting page index
            max_pages: Maximum pages to process (None = all)
            max_clips: Maximum clips to download (None = all)
            with_thumbnail: Download and embed thumbnails
            append_uuid: Append UUID to filenames
            progress_callback: Callback(message, progress_percent)
            delay: Delay between downloads in seconds
        
        Returns:
            Dict with 'success', 'failed', 'skipped', 'total_pages' counts
        """
        history = self.get_history(account_name)
        stats = {'success': 0, 'failed': 0, 'skipped': 0, 'total_pages': 0}
        
        # Update API client token
        self.api_client.update_session_token(session_token)
        
        current_page = start_page
        pages_processed = 0
        
        while True:
            # Check max_pages limit
            if max_pages is not None and pages_processed >= max_pages:
                logger.info(f"Reached max_pages limit: {max_pages}")
                break
            
            # Check max_clips limit
            if max_clips is not None and (stats['success'] + stats['skipped']) >= max_clips:
                logger.info(f"Reached max_clips limit: {max_clips}")
                break
            
            if progress_callback:
                progress_callback(f"Đang tải trang {current_page}...", 0)
            
            # Fetch one page of clips
            try:
                if use_create_page:
                    # Fetch from /create feed (one page)
                    api_clips, last_page, has_more = self.api_client.fetch_create_clips_paginated(
                        start_page=current_page, 
                        max_pages=1
                    )
                else:
                    # Fetch from profile (one page)
                    api_clips, last_page, has_more = self.api_client.fetch_profile_clips(
                        profile_name, 
                        start_page=current_page, 
                        max_pages=1
                    )
                
                if not api_clips:
                    logger.info(f"No more clips at page {current_page}")
                    break
                
                clips = [SongClip.from_api_response(clip) for clip in api_clips]
                stats['total_pages'] += 1
                pages_processed += 1
                
                logger.info(f"Page {current_page}: {len(clips)} clips")
                
                # Download clips from this page
                for idx, clip in enumerate(clips, 1):
                    # Check max_clips limit before processing each clip
                    if max_clips is not None and (stats['success'] + stats['skipped']) >= max_clips:
                        logger.info(f"Reached max_clips limit during page processing: {max_clips}")
                        break
                    
                    if progress_callback:
                        msg = f"Trang {current_page} - {idx}/{len(clips)}: {clip.title}"
                        progress_callback(msg, 0)
                    
                    # Skip if already downloaded
                    if history.is_downloaded(clip.id):
                        stats['skipped'] += 1
                        logger.debug(f"Skipped (already downloaded): {clip.title}")
                        continue
                    
                    # Download clip
                    success = self.download_clip(
                        session_token, clip, output_dir,
                        with_thumbnail, append_uuid, None
                    )
                    
                    if success:
                        history.add_download(clip.id)
                        stats['success'] += 1
                        # Save history after each successful download
                        self.save_histories()
                    else:
                        stats['failed'] += 1
                    
                    # Delay between downloads
                    if idx < len(clips) or has_more:
                        time.sleep(delay)
                
                # Move to next page
                if not has_more:
                    logger.info("No more pages available")
                    break
                
                current_page += 1
                
            except Exception as e:
                logger.error(f"Error fetching/downloading page {current_page}: {e}")
                stats['failed'] += 1
                break
        
        logger.info(f"Paginated batch download completed: {stats}")
        return stats
