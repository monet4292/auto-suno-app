"""
Smoke test: retrieve session token from /create and fetch first 3 pages via legacy fetch_my_clips_paginated
"""
import sys
from pathlib import Path
import traceback

# Ensure project root on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.session_manager import SessionManager
from legacy_modules.suno_batch_download import SunoBatchDownloader


def main():
    account_name = "thang"
    print(f"Starting smoke test (3 pages) for account: {account_name}")

    token = None
    driver = None
    try:
        token, driver = SessionManager.get_session_token_from_me_page(account_name)
        if not token:
            print("Failed to obtain session token from /create")
            return

        print(f"Got token (len={len(token)})")

        downloader = SunoBatchDownloader(session_token=token)
        print("Fetching up to 3 pages from /feed/v2 via fetch_my_clips_paginated...")
        clips, last_page, has_more = downloader.fetch_my_clips_paginated(start_page=0, max_pages=3)
        print(f"Fetched total {len(clips)} clips across up to 3 pages. last_page={last_page}, has_more={has_more}")

        # Print first 5 clip ids/titles
        print('\nFirst up to 5 clips:')
        for i, c in enumerate(clips[:5], 1):
            print(f"{i}. {c.get('title','N/A')} (id={c.get('id','N/A')})")

    except Exception as e:
        print("Exception during smoke test:")
        traceback.print_exc()

    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed")
            except Exception:
                pass


if __name__ == '__main__':
    main()
