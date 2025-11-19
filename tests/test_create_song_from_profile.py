import os
import time
import pytest
from selenium.webdriver.common.by import By

from src.core.session_manager import SessionManager
from src.core.js_snippets import SET_REACT_VALUE_SCRIPT


@pytest.mark.skipif(os.environ.get('RUN_SUNO_CREATE_E2E') != '1', reason='Enable by setting RUN_SUNO_CREATE_E2E=1')
def test_create_song_from_profile_manual():
    """
    Manual E2E test: open Chrome with existing profile and fill the create form's title field using React native setter.
    This test is gated and will be skipped unless RUN_SUNO_CREATE_E2E=1 is set in the environment.

    Requirements to run locally:
    - Have a Chrome profile under `profiles/<account_name>` (default 'thang').
    - ChromeDriver available on PATH compatible with installed Chrome.
    """
    account_name = os.environ.get('TEST_SUNO_ACCOUNT', 'thang')

    token, driver = SessionManager.get_session_token_from_me_page(account_name)
    assert driver is not None, f"Could not open browser for account {account_name}. Ensure profile exists and is not locked."

    try:
        # Try several selectors to locate a title input (site may change selectors)
        selectors = [
            'input[name="title"]',
            'input[placeholder*="Title"]',
            'input[placeholder*="title"]',
            'textarea[name="title"]',
            'input[type="text"]'
        ]
        el = None
        for sel in selectors:
            try:
                el = driver.find_element('css selector', sel)
                if el:
                    break
            except Exception:
                el = None
        assert el is not None, "Could not find title input on the create page."

        test_title = f"E2E Test Song {int(time.time())}"
        # Use the React native setter snippet to set the value
        driver.execute_script(SET_REACT_VALUE_SCRIPT, el, test_title)
        time.sleep(1)

        # Verify the value was set
        value = el.get_attribute('value')
        assert value == test_title or test_title in value, f"Title not set correctly (got: {value})"

        # Do not click create by default; this is a dry run to the confirmation point
        # If you want to auto-submit, set AUTO_SUBMIT=1 in environment (not recommended)
        if os.environ.get('AUTO_SUBMIT') == '1':
            # Attempt to find and click create button
            try:
                create_btn = driver.find_element('css selector', 'button.create')
                create_btn.click()
                time.sleep(2)
            except Exception:
                pytest.skip('Create button not found; skipping auto-submit')

    finally:
        try:
            driver.quit()
        except Exception:
            pass
