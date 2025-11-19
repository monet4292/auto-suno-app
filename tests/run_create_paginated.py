import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.session_manager import SessionManager
from src.core.suno_api_client import SunoApiClient

account = 'thang'
print('\nGetting session token from /create...')
token, driver = SessionManager.get_session_token_from_me_page(account)
if not token:
    print('No token')
    if driver:
        driver.quit()
    raise SystemExit(1)

print('Token length:', len(token))
api = SunoApiClient(session_token=token)

print('\nFetching paginated clips from /create...')
clips, last_page, has_more = api.fetch_create_clips_paginated()
print(f'Fetched {len(clips)} clips, last_page={last_page}, has_more={has_more}')

# show first 3 titles
for i, c in enumerate(clips[:3], 1):
    print(f"{i}. {c.get('title')} ({c.get('id')})")

if driver:
    input('\nPress Enter to close browser...')
    driver.quit()
print('Done')
