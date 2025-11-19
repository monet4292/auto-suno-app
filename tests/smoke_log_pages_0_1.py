"""
Fetch /feed/v2 pages 0 and 1 and write titles and ids to log.txt
"""
import sys
from pathlib import Path
import traceback

# ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.session_manager import SessionManager
from legacy_modules.suno_batch_download import SunoBatchDownloader


def main():
    account_name = "thang"
    out_path = Path("log.txt")

    print(f"Starting fetch of pages 0 and 1 for account: {account_name}")
    token = None
    driver = None

    try:
        token, driver = SessionManager.get_session_token_from_me_page(account_name)
        if not token:
            print("Failed to obtain session token from /create")
            return

        print(f"Got token (len={len(token)})")
        downloader = SunoBatchDownloader(session_token=token)

        clips, last_page, has_more = downloader.fetch_my_clips_paginated(start_page=0, max_pages=2)
        total = len(clips)
        print(f"Fetched total {total} clips from pages 0..1. last_page={last_page}, has_more={has_more}")

        # Ensure we have up to 40 entries
        entries = clips[:40]

        with out_path.open('w', encoding='utf-8') as f:
            f.write(f"Fetched {len(entries)} clips from pages 0 and 1\n")
            f.write("\n")
            for idx, c in enumerate(entries, 1):
                title = c.get('title', '').strip()
                cid = c.get('id', '')
                f.write(f"{idx}. {title} — {cid}\n")

        print(f"Wrote {len(entries)} entries to {out_path.resolve()}")

    except Exception as e:
        print("Exception during fetch:")
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
