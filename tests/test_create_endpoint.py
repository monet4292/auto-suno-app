"""
Test for changing from /me to /create endpoint
Testing new functionality to fetch songs from suno.com/create page
"""
import os
import sys
from pathlib import Path

import pytest

# Skip these live-browser tests unless explicitly enabled.
RUN_LIVE_SUNO_TESTS = os.getenv("RUN_SUNO_LIVE_TESTS") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_LIVE_SUNO_TESTS,
    reason="Requires RUN_SUNO_LIVE_TESTS=1 plus a configured Chrome profile",
)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.session_manager import SessionManager
from src.core.suno_api_client import SunoApiClient
from src.core.download_manager import DownloadManager
from src.utils.logger import logger


def test_session_token_from_create():
    """Test getting session token from /create page"""
    print("\n=== Test 1: Get Session Token from /create ===")
    
    account_name = "thang"
    
    # Try to get session token from /create
    token, driver = SessionManager.get_session_token_from_create_page(account_name)
    
    if token:
        print(f"✓ Successfully retrieved token from /create")
        print(f"  Token length: {len(token)}")
        print(f"  Token preview: {token[:20]}...")
    else:
        print("✗ Failed to retrieve token from /create")
    
    # Close driver if opened
    if driver:
        # Only wait for input when running the module directly; avoid blocking pytest
        if __name__ == "__main__":
            input("Press Enter to close browser...")
        driver.quit()
    
    return token is not None


def test_fetch_clips_from_create():
    """Test fetching clips from /create endpoint"""
    print("\n=== Test 2: Fetch Clips from /create ===")
    
    account_name = "thang"
    
    # Get session token first
    token = SessionManager.get_session_token(account_name)
    
    if not token:
        print("✗ No session token available")
        return False
    
    print(f"✓ Using session token (length: {len(token)})")
    
    # Initialize API client
    api_client = SunoApiClient(session_token=token)
    
    # Fetch clips from create endpoint
    clips = api_client.fetch_create_clips()
    
    if clips:
        print(f"✓ Successfully fetched {len(clips)} clips from /create")
        
        # Display first few clips
        for i, clip in enumerate(clips[:3]):
            print(f"\n  Clip {i+1}:")
            print(f"    ID: {clip.get('id', 'N/A')}")
            print(f"    Title: {clip.get('title', 'N/A')}")
            print(f"    Status: {clip.get('status', 'N/A')}")
    else:
        print("✗ No clips found from /create")
    
    return len(clips) > 0 if clips else False


def test_download_manager_with_create():
    """Test DownloadManager with /create endpoint"""
    print("\n=== Test 3: Download Manager with /create ===")
    
    account_name = "thang"
    
    # Get session token
    token = SessionManager.get_session_token(account_name)
    
    if not token:
        print("✗ No session token available")
        return False
    
    # Initialize download manager
    download_manager = DownloadManager()
    
    # Fetch clips using new method
    clips = download_manager.fetch_clips(
        session_token=token,
        use_create_page=True
    )
    
    if clips:
        print(f"✓ DownloadManager fetched {len(clips)} clips from /create")
        
        # Display first few clips
        for i, clip in enumerate(clips[:3]):
            print(f"\n  Clip {i+1}:")
            print(f"    ID: {clip.id}")
            print(f"    Title: {clip.title}")
            print(f"    Audio URL: {clip.audio_url[:50] if clip.audio_url else 'N/A'}...")
    else:
        print("✗ No clips fetched by DownloadManager")
    
    return len(clips) > 0


def test_compare_me_vs_create():
    """Compare clips from /me vs /create"""
    print("\n=== Test 4: Compare /me vs /create ===")
    
    account_name = "thang"
    
    # Get session token
    token = SessionManager.get_session_token(account_name)
    
    if not token:
        print("✗ No session token available")
        return False
    
    # Initialize API client
    api_client = SunoApiClient(session_token=token)
    
    # Fetch from /me (old method)
    me_clips = api_client.fetch_my_clips()
    print(f"  /me endpoint: {len(me_clips)} clips")
    
    # Fetch from /create (new method)
    create_clips = api_client.fetch_create_clips()
    print(f"  /create endpoint: {len(create_clips)} clips")
    
    # Compare
    if len(create_clips) >= len(me_clips):
        print(f"✓ /create has {len(create_clips) - len(me_clips)} more clips than /me")
    else:
        print(f"⚠ /create has {len(me_clips) - len(create_clips)} fewer clips than /me")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing /create endpoint implementation")
    print("=" * 60)
    
    results = {
        "Session Token from /create": False,
        "Fetch Clips from /create": False,
        "Download Manager with /create": False,
        "Compare /me vs /create": False
    }
    
    try:
        # Test 1: Session token from /create page
        # Note: This requires new implementation
        # results["Session Token from /create"] = test_session_token_from_create()
        print("\n⚠ Test 1 skipped - requires implementation of get_session_token_from_create_page()")
        
        # Test 2: Fetch clips from /create endpoint
        # Note: This requires new API method
        # results["Fetch Clips from /create"] = test_fetch_clips_from_create()
        print("\n⚠ Test 2 skipped - requires implementation of fetch_create_clips()")
        
        # Test 3: Download Manager with /create
        # Note: This requires updating DownloadManager
        # results["Download Manager with /create"] = test_download_manager_with_create()
        print("\n⚠ Test 3 skipped - requires implementation in DownloadManager")
        
        # Test 4: Compare results
        results["Compare /me vs /create"] = test_compare_me_vs_create()
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")


if __name__ == "__main__":
    main()
