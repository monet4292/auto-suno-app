"""
Session Manager - Manages Chrome sessions and authentication tokens
"""
import time
from pathlib import Path
from tkinter import Tk
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.settings import PROFILES_DIR, SUNO_URL, CHROME_OPTIONS
from src.utils import logger


class SessionManager:
    """Manages Chrome sessions and authentication tokens"""
    
    @staticmethod
    def _cleanup_profile_locks(profile_path: Path) -> None:
        """Remove leftover lock files to avoid Chrome refusing to start."""
        lock_candidates = (
            "SingletonLock",
            "SingletonLock.bak",
            "lockfile",
            "LOCK",
            "Chrome SingletonLock",
        )
        for lock_name in lock_candidates:
            target = profile_path / lock_name
            try:
                if target.exists():
                    target.unlink()
            except Exception:
                # best-effort cleanup, ignore if removal fails
                pass

    @staticmethod
    def _get_quarter_screen_size() -> tuple[int, int] | None:
        try:
            root = Tk()
            root.withdraw()
            width = max(640, root.winfo_screenwidth() // 2)
            height = max(480, root.winfo_screenheight() // 2)
            root.destroy()
            return width, height
        except Exception:
            return None

    @staticmethod
    def create_chrome_options(profile_path: Path, headless: bool = False) -> Options:
        """Create Chrome options with profile"""
        options = Options()
        options.add_argument(f'--user-data-dir={profile_path}')
        options.add_argument('--profile-directory=Default')
        
        for opt in CHROME_OPTIONS:
            options.add_argument(opt)
        
        if headless:
            options.add_argument('--headless=new')  # New headless mode
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--window-size=1920,1080')
        else:
            size = SessionManager._get_quarter_screen_size()
            if size:
                options.add_argument(f'--window-size={size[0]},{size[1]}')
        
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    @staticmethod
    def launch_browser(account_name: str, headless: bool = False) -> Optional[webdriver.Chrome]:
        """Launch browser with account profile"""
        profile_path = PROFILES_DIR / account_name
        profile_path.mkdir(parents=True, exist_ok=True)
        SessionManager._cleanup_profile_locks(profile_path)
        
        try:
            options = SessionManager.create_chrome_options(profile_path, headless)
            driver = webdriver.Chrome(options=options)
            
            # Anti-detection
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            driver.get(SUNO_URL)
            logger.info(f"Browser launched for account: {account_name}")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return None
    
    @staticmethod
    def get_session_token(account_name: str) -> Optional[str]:
        """Get session token from Chrome profile"""
        profile_path = PROFILES_DIR / account_name
        profile_path.mkdir(parents=True, exist_ok=True)
        
        driver = None
        try:
            logger.info(f"Opening browser to get session token...")
            options = SessionManager.create_chrome_options(profile_path, headless=False)
            driver = webdriver.Chrome(options=options)
            driver.get(SUNO_URL)
            
            # Wait for page load
            time.sleep(3)
            
            # Get cookies
            cookies = driver.get_cookies()
            
            # Find __session cookie
            for cookie in cookies:
                if cookie['name'] == '__session':
                    token = cookie['value']
                    logger.info(f"✓ Session token retrieved for: {account_name} (length: {len(token)})")
                    return token
            
            logger.warning(f"No __session cookie found")
            logger.debug(f"Available cookies: {[c['name'] for c in cookies]}")
            return None
                    
        except Exception as e:
            logger.error(f"Failed to get session token: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
    
    @staticmethod
    def get_session_token_from_me_page(account_name: str) -> tuple[Optional[str], Optional[webdriver.Chrome]]:
        """
        Open suno.com/create and retrieve session token
        Returns: (token, driver) - keep driver open for user interaction
        """
        profile_path = PROFILES_DIR / account_name
        profile_path.mkdir(parents=True, exist_ok=True)
        
        driver = None
        try:
            logger.info(f"Opening https://suno.com/create to get session token...")
            options = SessionManager.create_chrome_options(profile_path, headless=False)
            
            # Add more options to avoid profile lock issues
            options.add_argument('--disable-lock-screen-chrome-profile')
            options.add_argument('--disable-extensions')
            
            driver = webdriver.Chrome(options=options)
            
            # Anti-detection
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            # Navigate to /create page directly
            create_url = "https://suno.com/create"
            logger.info(f"Navigating to {create_url}...")
            driver.get(create_url)
            
            # Wait for page load
            time.sleep(5)  # Increase wait time for better loading
            
            # Get cookies
            cookies = driver.get_cookies()
            logger.info(f"Found {len(cookies)} cookies")
            
            # Find __session cookie
            for cookie in cookies:
                if cookie['name'] == '__session':
                    token = cookie['value']
                    logger.info(f"✓ Session token retrieved from /create (length: {len(token)})")
                    return token, driver  # Trả về cả driver để giữ browser mở
            
            logger.warning(f"No __session cookie found on /create")
            logger.debug(f"Available cookies: {[c['name'] for c in cookies]}")
            return None, driver
                    
        except Exception as e:
            error_msg = str(e)
            if "Chrome instance exited" in error_msg:
                logger.error(f"Chrome profile is locked. Close all Chrome windows using profile '{account_name}' and try again.")
            else:
                logger.error(f"Failed to get session token from /create: {error_msg}")
            
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            return None, None
    
    @staticmethod
    def verify_session(account_name: str) -> bool:
        """Verify if session is still valid"""
        token = SessionManager.get_session_token(account_name)
        return token is not None

    # Backwards-compatible alias: some tests/consumers expect this name
    @staticmethod
    def get_session_token_from_create_page(account_name: str) -> tuple[Optional[str], Optional[webdriver.Chrome]]:
        """Alias for get_session_token_from_me_page to preserve older API name."""
        return SessionManager.get_session_token_from_me_page(account_name)
