"""
Smoke test for paginated download with mock data
Tests the DownloadManager.batch_download_paginated flow without real network calls
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.download_manager import DownloadManager
from src.models import SongClip


def create_mock_clip(page_num: int, clip_num: int):
    """Create a mock clip response"""
    clip_id = f"clip-p{page_num}-{clip_num:02d}"
    return {
        'id': clip_id,
        'title': f"Song Page{page_num} #{clip_num}",
        'audio_url': f"https://example.com/audio/{clip_id}.mp3",
        'image_url': f"https://example.com/image/{clip_id}.jpg",
        'display_name': "Test Artist",
        'status': 'complete',
        'metadata': {'tags': 'test,mock'},
        'created_at': '2025-11-09T00:00:00Z'
    }


def test_paginated_download():
    """Test paginated download flow with 3 pages of mock data"""
    
    print("=" * 70)
    print("Smoke Test: Paginated Download with Mock Data")
    print("=" * 70)
    
    # Create temp directory for downloads
    temp_dir = Path(tempfile.mkdtemp(prefix="suno_test_"))
    print(f"\nTemp directory: {temp_dir}")
    
    try:
        # Setup mock data: 3 pages with 5 clips each
        mock_pages = [
            [create_mock_clip(0, i) for i in range(5)],  # Page 0
            [create_mock_clip(1, i) for i in range(5)],  # Page 1
            [create_mock_clip(2, i) for i in range(5)],  # Page 2
        ]
        
        page_counter = {'current': 0}
        
        def mock_fetch_create_clips_paginated(start_page=0, max_pages=1):
            """Mock API fetch that returns one page at a time"""
            page = page_counter['current']
            if page >= len(mock_pages):
                return [], page - 1, False
            
            clips = mock_pages[page]
            has_more = page < len(mock_pages) - 1
            page_counter['current'] += 1
            
            print(f"  [Mock API] Fetched page {page}: {len(clips)} clips, has_more={has_more}")
            return clips, page, has_more
        
        def mock_download_audio(clip_data, output_dir, append_uuid):
            """Mock audio download - create empty file"""
            clip_id = clip_data['id']
            title = clip_data['title']
            filename = f"{title}__ID__{clip_id}.mp3" if append_uuid else f"{title}.mp3"
            filepath = Path(output_dir) / filename
            filepath.write_text("mock audio data")
            print(f"    [Mock Download] {filename}")
            return str(filepath)
        
        def mock_download_thumbnail(clip_data, output_dir):
            """Mock thumbnail download"""
            return None
        
        def mock_embed_metadata(audio_path, clip_data, thumbnail_path):
            """Mock metadata embedding"""
            pass
        
        # Create DownloadManager and patch methods
        manager = DownloadManager()
        
        with patch.object(manager.api_client, 'fetch_create_clips_paginated', side_effect=mock_fetch_create_clips_paginated):
            with patch.object(manager.file_downloader, 'download_audio', side_effect=mock_download_audio):
                with patch.object(manager.file_downloader, 'download_thumbnail', side_effect=mock_download_thumbnail):
                    with patch.object(manager.metadata_handler, 'embed_metadata', side_effect=mock_embed_metadata):
                        
                        print("\n" + "=" * 70)
                        print("Starting paginated download (3 pages, 5 clips each)")
                        print("=" * 70 + "\n")
                        
                        # Progress callback
                        def progress_cb(msg, pct):
                            print(f"  [Progress] {msg}")
                        
                        # Run paginated download
                        stats = manager.batch_download_paginated(
                            account_name="test_account",
                            session_token="mock_token",
                            output_dir=temp_dir,
                            profile_name=None,
                            use_create_page=True,
                            start_page=0,
                            max_pages=None,
                            with_thumbnail=False,
                            append_uuid=True,
                            progress_callback=progress_cb,
                            delay=0  # No delay in test
                        )
        
        print("\n" + "=" * 70)
        print("Results:")
        print("=" * 70)
        print(f"  Success:      {stats['success']}")
        print(f"  Failed:       {stats['failed']}")
        print(f"  Skipped:      {stats['skipped']}")
        print(f"  Total Pages:  {stats['total_pages']}")
        print(f"  Expected:     15 clips (3 pages × 5 clips)")
        
        # Verify files created
        files = list(temp_dir.glob("*.mp3"))
        print(f"\n  Files created: {len(files)}")
        
        # Test assertions
        assert stats['success'] == 15, f"Expected 15 successful downloads, got {stats['success']}"
        assert stats['total_pages'] == 3, f"Expected 3 pages, got {stats['total_pages']}"
        assert stats['failed'] == 0, f"Expected 0 failures, got {stats['failed']}"
        assert len(files) == 15, f"Expected 15 files, got {len(files)}"
        
        print("\n" + "=" * 70)
        print("✅ All assertions passed!")
        print("=" * 70)
        
        # Test resume functionality
        print("\n" + "=" * 70)
        print("Testing Resume Functionality")
        print("=" * 70 + "\n")
        
        # Reset page counter
        page_counter['current'] = 0
        
        # Run again - should skip all 15 clips
        with patch.object(manager.api_client, 'fetch_create_clips_paginated', side_effect=mock_fetch_create_clips_paginated):
            with patch.object(manager.file_downloader, 'download_audio', side_effect=mock_download_audio):
                with patch.object(manager.file_downloader, 'download_thumbnail', side_effect=mock_download_thumbnail):
                    with patch.object(manager.metadata_handler, 'embed_metadata', side_effect=mock_embed_metadata):
                        
                        stats2 = manager.batch_download_paginated(
                            account_name="test_account",
                            session_token="mock_token",
                            output_dir=temp_dir,
                            profile_name=None,
                            use_create_page=True,
                            start_page=0,
                            max_pages=None,
                            with_thumbnail=False,
                            append_uuid=True,
                            progress_callback=None,
                            delay=0
                        )
        
        print(f"\n  Resume Results:")
        print(f"    Success:  {stats2['success']}")
        print(f"    Skipped:  {stats2['skipped']}")
        
        assert stats2['skipped'] == 15, f"Expected 15 skipped on resume, got {stats2['skipped']}"
        assert stats2['success'] == 0, f"Expected 0 new downloads on resume, got {stats2['success']}"
        
        print("\n✅ Resume test passed!")
        
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n🗑️  Cleaned up temp directory: {temp_dir}")
    
    print("\n" + "=" * 70)
    print("🎉 Smoke test completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    test_paginated_download()
