"""
Application Settings and Configuration
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
PROFILES_DIR = BASE_DIR / "profiles"
DOWNLOADS_DIR = BASE_DIR / "downloads"
DATA_DIR = BASE_DIR / "data"

# Data files
ACCOUNTS_FILE = DATA_DIR / "suno_accounts.json"
HISTORY_FILE = DATA_DIR / "download_history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
QUEUE_STATE_FILE = DATA_DIR / "queue_state.json"
SONG_CREATION_HISTORY_FILE = DATA_DIR / "song_creation_history.json"

# Ensure directories exist
PROFILES_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Application settings
APP_NAME = "Suno Account Manager"
APP_VERSION = "2.0.0"
APP_WIDTH = 1400
APP_HEIGHT = 850

# UI Theme
THEME = "dark-blue"
APPEARANCE_MODE = "dark"  # "dark", "light", "system"

# Colors
COLORS = {
    "primary": "#1f538d",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "dark": "#2c3e50",
    "light": "#ecf0f1"
}

# Suno API
SUNO_URL = "https://suno.com"
SUNO_API_URL = "https://studio-api.prod.suno.com/api"

# Chrome options
CHROME_OPTIONS = [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage'
]

# Download settings
DEFAULT_DOWNLOAD_LIMIT = 10
MAX_CONCURRENT_DOWNLOADS = 3
DOWNLOAD_TIMEOUT = 300  # seconds
RETRY_ATTEMPTS = 3
DELAY_BETWEEN_DOWNLOADS = 2  # seconds

# Session settings
SESSION_TOKEN_EXPIRY = 3600 * 24  # 24 hours
AUTO_REFRESH_SESSION = True
