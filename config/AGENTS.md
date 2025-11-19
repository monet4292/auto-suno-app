# AGENTS.md

**Audience:** AI coding agents, all developers  
**Applies to:** `config/**/*.py`  
**Scope:** Configuration hierarchy, path constants, settings precedence  
**Last reviewed:** 2025-11-10  
**Owners:** Core team

---

## Configuration Hierarchy

### File Structure

```
config/
├── __init__.py              # Empty (package marker)
├── settings.py              # Central constants (paths, URLs, app settings)
├── style_config.py          # UI theme, colors, fonts
└── suno_selectors_from_clicknium.py  # CSS selectors for automation
```

**Rule**: Never duplicate constants. Import from `config.settings` or `config.style_config`.

---

## Path Constants

### Directory Paths

**Source of truth**: `config/settings.py`

```python
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent  # Project root
PROFILES_DIR = BASE_DIR / "profiles"
DOWNLOADS_DIR = BASE_DIR / "downloads"
DATA_DIR = BASE_DIR / "data"

# Data files
ACCOUNTS_FILE = DATA_DIR / "suno_accounts.json"
HISTORY_FILE = DATA_DIR / "download_history.json"
QUEUE_STATE_FILE = DATA_DIR / "queue_state.json"
SONG_CREATION_HISTORY_FILE = DATA_DIR / "song_creation_history.json"
```

**Usage everywhere**:
```python
# ✅ CORRECT: Import from config
from config.settings import PROFILES_DIR, ACCOUNTS_FILE

def load_profile(account_name: str):
    profile_path = PROFILES_DIR / account_name
    # ...

# ❌ WRONG: Hardcode paths
def load_profile(account_name: str):
    profile_path = Path("profiles") / account_name  # NO!
```

**Why?**
- Single source of truth
- Easy to change (edit one file)
- Testable (mock `settings.PROFILES_DIR`)

---

## JSON Persistence

### Name-as-Key Pattern

**Critical**: Account name is JSON KEY, not in value.

```python
# suno_accounts.json structure
{
  "account_name": {  # ← Name is KEY
    "email": "user@example.com",
    "created_at": "2025-11-09T10:00:00",
    "last_used": "2025-11-09T15:30:00",
    "status": "active"
    # NO "name" field here!
  }
}
```

**Loading pattern** (inject key into model):
```python
from config.settings import ACCOUNTS_FILE
from src.utils.helpers import load_json

data = load_json(ACCOUNTS_FILE, {})
accounts = {}
for name, info in data.items():
    info['name'] = name  # ADD name from key
    accounts[name] = Account.from_dict(info)
```

**Saving pattern** (remove key from value):
```python
data = {}
for name, account in accounts.items():
    account_dict = account.to_dict()
    account_dict.pop('name', None)  # REMOVE name (it's the key)
    data[name] = account_dict

save_json(ACCOUNTS_FILE, data)
```

**Why this pattern?**
- Prevents duplication (name stored once)
- Natural indexing (fast lookup by name)
- Consistency across all JSON files

**Used in**:
- `suno_accounts.json` (account name as key)
- `download_history.json` (account name as key)
- `queue_state.json` (queues array, not keyed)
- `song_creation_history.json` (array, not keyed)

---

## Settings Precedence

### Application Settings

```python
# config/settings.py

# Application metadata
APP_NAME = "Suno Account Manager"
APP_VERSION = "2.0.0"
APP_WIDTH = 1400
APP_HEIGHT = 850

# UI Theme
THEME = "dark-blue"
APPEARANCE_MODE = "dark"  # "dark" | "light" | "system"
```

**Runtime override** (not recommended):
```python
# Only in tests or special cases
import config.settings as settings
settings.APP_WIDTH = 1600  # Overrides default
```

### Suno API Settings

```python
# URLs (never change without verification)
SUNO_URL = "https://suno.com"
SUNO_API_URL = "https://studio-api.prod.suno.com/api"

# Chrome options (anti-detection)
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
```

**Usage in managers**:
```python
from config.settings import SUNO_API_URL, RETRY_ATTEMPTS, DOWNLOAD_TIMEOUT

class DownloadManager:
    def fetch_clips(self, token: str):
        url = f"{SUNO_API_URL}/feed/v2"
        for attempt in range(RETRY_ATTEMPTS):
            response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
            # ...
```

---

## Style Configuration

### UI Theme & Colors

**Source**: `config/style_config.py`

```python
# Colors
COLORS = {
    "primary": "#1f538d",
    "primary_hover": "#164270",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "dark": "#2c3e50",
    "light": "#ecf0f1"
}

# Fonts
FONTS = {
    "title": ("Arial", 20, "bold"),
    "heading": ("Arial", 16, "bold"),
    "body": ("Arial", 12),
    "button": ("Arial", 12, "bold"),
    "code": ("Courier New", 10)
}

# Responsive design
WINDOW_SIZES = {
    "small": (1200, 700),
    "medium": (1400, 850),  # Default
    "large": (1600, 1000)
}
```

**Usage in UI**:
```python
from config.style_config import COLORS, FONTS

class YourPanel(ctk.CTkFrame):
    def _create_widgets(self):
        self.title_label = ctk.CTkLabel(
            self,
            text="Panel Title",
            font=FONTS["title"],
            text_color=COLORS["primary"]
        )
        
        self.submit_button = ctk.CTkButton(
            self,
            text="Submit",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["button"]
        )
```

---

## Suno Selectors

### CSS Selectors for Automation

**Source**: `config/suno_selectors_from_clicknium.py`

Contains CSS selectors extracted from Suno.com for browser automation.

```python
class SunoSelectors:
    # Form inputs
    LYRICS_TEXTAREA = "textarea[placeholder*='lyrics']"
    STYLES_INPUT = "input[placeholder*='style']"
    TITLE_INPUT = "input[placeholder*='title']"
    
    # Buttons
    CREATE_BUTTON = "button:has-text('Create')"
    CUSTOM_MODE_BUTTON = "button[data-mode='custom']"
    
    # Results
    SONG_CARD = "div[data-testid='song-card']"
    SONG_URL_LINK = "a[href^='/song/']"
```

**Usage in core layer**:
```python
from config.suno_selectors_from_clicknium import SunoSelectors
from selenium.webdriver.common.by import By

# Find elements
lyrics_input = driver.find_element(By.CSS_SELECTOR, SunoSelectors.LYRICS_TEXTAREA)
create_button = driver.find_element(By.CSS_SELECTOR, SunoSelectors.CREATE_BUTTON)
```

**Why centralized?**
- Suno.com updates selectors → change one file
- Avoid selector duplication across modules
- Easy to maintain/test

---

## Directory Initialization

### Auto-Create Directories

`config/settings.py` ensures directories exist on import:

```python
# Ensure directories exist
PROFILES_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
```

**Effect**: First import of `config.settings` creates directories if missing.

**Why?**
- Clean project structure on first run
- No manual setup required
- Safe (idempotent with `exist_ok=True`)

---

## Environment Variables

### Not Used (Yet)

Current design: All config in Python files.

**Future consideration** (v3.0+):
```python
# config/settings.py (hypothetical)
import os
from pathlib import Path

# Allow override via env vars
BASE_DIR = Path(os.getenv("SUNO_BASE_DIR", Path(__file__).parent.parent))
SUNO_API_URL = os.getenv("SUNO_API_URL", "https://studio-api.prod.suno.com/api")
```

**Why not now?**
- Simple Python config sufficient for single-machine desktop app
- No deployment environments (dev/staging/prod)
- User can edit `settings.py` directly

**When to add**:
- Multi-user deployments
- Docker containerization
- CI/CD pipelines

---

## Configuration Testing

### Mock Config in Tests

```python
from unittest.mock import patch
import pytest

@patch('config.settings.PROFILES_DIR', '/tmp/test_profiles')
@patch('config.settings.ACCOUNTS_FILE', '/tmp/test_accounts.json')
def test_account_manager():
    """
    Tests use temp directories to avoid touching real data.
    """
    manager = AccountManager()
    # Test with mocked paths...
```

### Fixture for Temp Paths

```python
# tests/fixtures/temp_config.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_config(monkeypatch):
    """Provides temporary paths for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        monkeypatch.setattr('config.settings.BASE_DIR', tmp_path)
        monkeypatch.setattr('config.settings.PROFILES_DIR', tmp_path / 'profiles')
        monkeypatch.setattr('config.settings.DATA_DIR', tmp_path / 'data')
        monkeypatch.setattr('config.settings.ACCOUNTS_FILE', tmp_path / 'data' / 'accounts.json')
        
        yield tmp_path
```

---

## Common Pitfalls

### ❌ Hardcoded Paths

```python
# WRONG: Hardcoded path
def load_accounts():
    with open("data/suno_accounts.json") as f:
        return json.load(f)
```

```python
# CORRECT: Import from config
from config.settings import ACCOUNTS_FILE
from src.utils.helpers import load_json

def load_accounts():
    return load_json(ACCOUNTS_FILE, {})
```

### ❌ Duplicate Constants

```python
# WRONG: Defining in multiple files
# download_manager.py
SUNO_API_URL = "https://studio-api.prod.suno.com/api"

# account_manager.py
SUNO_API_URL = "https://studio-api.prod.suno.com/api"  # Duplication!
```

```python
# CORRECT: Import from config
from config.settings import SUNO_API_URL
```

### ❌ Relative Path Assumptions

```python
# WRONG: Assumes current directory
profile_path = Path("profiles") / account_name  # Breaks if run from subdirectory
```

```python
# CORRECT: Use BASE_DIR
from config.settings import PROFILES_DIR
profile_path = PROFILES_DIR / account_name  # Always correct
```

---

## Entry Points

| File | Purpose | Key Exports |
|------|---------|-------------|
| `settings.py` | App config, paths, API URLs | `BASE_DIR`, `PROFILES_DIR`, `DOWNLOADS_DIR`, `DATA_DIR`, `ACCOUNTS_FILE`, `SUNO_URL`, `SUNO_API_URL`, `CHROME_OPTIONS`, download settings |
| `style_config.py` | UI theme, colors, fonts | `COLORS`, `FONTS`, `WINDOW_SIZES` |
| `suno_selectors_from_clicknium.py` | CSS selectors | `SunoSelectors` class |

---

## Cross-References

- **Usage in Core**: See `src/core/AGENTS.md#session-patterns` for profile path usage
- **Usage in UI**: See `src/ui/AGENTS.md#customtkinter-conventions` for style config usage
- **JSON patterns**: See `src/core/AGENTS.md#data-models` for name-as-key pattern
- **Testing**: See `tests/AGENTS.md#fixture-conventions` for config mocking

---

**Questions?** Check root `AGENTS.md` for general project conventions.
