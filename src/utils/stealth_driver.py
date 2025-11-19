"""
Stealth WebDriver Setup - Anti-detection cho Selenium
Tránh CAPTCHA và bot detection trên Suno.com
"""
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# User-Agent pool (Chrome trên Windows 11)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
]


def create_stealth_driver(profile_path: Path, headless: bool = False) -> webdriver.Chrome:
    """
    Tạo ChromeDriver với anti-detection tối đa.
    
    Args:
        profile_path: Đường dẫn profile Chrome (giữ session/cookies)
        headless: Chạy chế độ ẩn (tăng risk CAPTCHA, không khuyến khích)
    
    Returns:
        webdriver.Chrome với stealth options
    """
    options = Options()
    
    # 1. User profile (quan trọng nhất - giữ session)
    options.add_argument(f'--user-data-dir={profile_path}')
    
    # 2. User-Agent rotation
    ua = random.choice(USER_AGENTS)
    options.add_argument(f'--user-agent={ua}')
    
    # 3. Anti-detection flags
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 4. Thêm các flag giống browser thật
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')  # Tránh một số fingerprint
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    
    # 5. Preferences (tắt các thông báo automation)
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
    }
    options.add_experimental_option('prefs', prefs)
    
    # 6. Headless mode (nếu cần, nhưng dễ bị phát hiện hơn)
    if headless:
        options.add_argument('--headless=new')  # Chrome headless mode mới
        options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    
    # 7. Inject stealth JS scripts
    _inject_stealth_scripts(driver)
    
    return driver


def _inject_stealth_scripts(driver: webdriver.Chrome):
    """
    Inject các script JS để ẩn dấu hiệu automation.
    Chạy ngay sau khi tạo driver, trước khi navigate.
    """
    # Script 1: Ẩn navigator.webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    # Script 2: Override plugins/languages để giống browser thật
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'vi-VN', 'vi']
            });
        '''
    })
    
    # Script 3: Chrome runtime mock
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            window.chrome = {
                runtime: {}
            };
        '''
    })
    
    # Script 4: Permission API mock
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        '''
    })


def add_human_delays():
    """
    Trả về random delay giống hành vi người dùng thật.
    Dùng giữa các thao tác: click, fill form, scroll.
    Range: 3-5 giây để tránh CAPTCHA khi submit.
    """
    import time
    delay = random.uniform(3.0, 5.0)
    time.sleep(delay)
    return delay
