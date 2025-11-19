# AGENTS.md

**Audience:** AI coding agents, developers working on business logic  
**Applies to:** `src/core/**/*.py`  
**Scope:** Manager lifecycle, session patterns, queue workflows, API integration, browser automation  
**Last reviewed:** 2025-11-10  
**Owners:** Core team, backend developers

---

## Architecture Overview

### Clean Architecture Layers

Core layer sits between UI (presentation) and Models (domain):

```
UI Layer (src/ui/) 
    ↓ depends on
Core Layer (src/core/) ← YOU ARE HERE
    ↓ depends on
Models Layer (src/models/)
    ↓ uses
Utils Layer (src/utils/)
```

**Critical Rule**: Core NEVER imports from UI. Core provides interfaces (callbacks) that UI implements.

### Component Map

| Manager | Responsibility | Key Dependencies |
|---------|---------------|------------------|
| `AccountManager` | CRUD for accounts, JSON persistence | Models (Account), Utils (helpers) |
| `SessionManager` | Chrome profile launch, token extraction | Utils (stealth_driver), Config (PROFILES_DIR) |
| `QueueManager` | Queue CRUD, state persistence | Models (QueueEntry), Config (QUEUE_STATE_FILE) |
| `BatchSongCreator` | Multi-queue execution engine | SessionManager, SunoFormFiller, SunoApiClient |
| `DownloadManager` | Download orchestration, history | SessionManager, SunoApiClient, Utils (file_downloader) |
| `SongCreationHistoryManager` | Creation history, CSV export | Models (SongCreationRecord), Config (SONG_CREATION_HISTORY_FILE) |

---

## Manager Lifecycle

### Singleton Pattern

**All managers are created once** in `MainWindow.__init__()` and **injected into panels**.

```python
# ✅ CORRECT: Create in MainWindow
class MainWindow(ctk.CTk):
    def __init__(self):
        self.account_manager = AccountManager()
        self.session_manager = SessionManager()
        self.queue_manager = QueueManager()
        
        # Inject into panels
        self.account_panel = AccountPanel(
            parent=content_frame,
            account_manager=self.account_manager,
            session_manager=self.session_manager
        )

# ❌ WRONG: Never create inside panels
class AccountPanel(ctk.CTkFrame):
    def __init__(self, parent):
        self.account_manager = AccountManager()  # Creates duplicate instance!
```

**Why singleton-like?**
- Managers hold shared state (accounts dict, queues dict)
- Multiple instances cause state divergence
- Testability: inject mock managers in tests

### Constructor Patterns

```python
class YourManager:
    def __init__(self):
        """
        Managers initialize in __init__:
        1. Load persisted state from JSON
        2. Initialize empty collections
        3. Set up logging
        
        Do NOT:
        - Launch browsers (lazy on-demand)
        - Make network calls (lazy on-demand)
        - Create heavy resources
        """
        self.data = self._load_state()
        self.logger = Logger()
```

---

## Session Patterns

### Chrome Profile Management

**Why profiles?** Suno uses Clerk.com auth with critical data in `localStorage` (not just cookies).

```
profiles/{account_name}/
└── Default/
    ├── Cookies              # __session JWT token
    ├── Local Storage/       # __clerk_environment (CRITICAL!)
    └── Preferences          # Chrome settings
```

### Token Extraction

```python
# session_manager.py pattern
def get_session_token_from_me_page(self, account_name: str) -> Tuple[str, webdriver.Chrome]:
    """
    1. Launch Chrome with --user-data-dir=profiles/{account_name}
    2. Navigate to suno.com/me
    3. Wait 3s for cookies to load
    4. Extract __session cookie
    5. Return (token, driver) ← IMPORTANT: Keep driver open!
    
    Why keep driver open?
    - Session stays valid while browser open
    - User may need to re-login if CAPTCHA
    - Caller responsible for closing driver
    """
    profile_path = PROFILES_DIR / account_name
    driver = create_stealth_driver(profile_path, headless=False)
    driver.get(f"{SUNO_URL}/me")
    time.sleep(3)
    
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie['name'] == '__session':
            return cookie['value'], driver
    
    raise SessionTokenError(f"No __session cookie for {account_name}")
```

### Anti-Detection (Stealth Driver)

See `src/utils/stealth_driver.py` for implementation. Core principles:

1. **Hide navigator.webdriver** via CDP injection
2. **Mock plugins/languages** to look like real browser
3. **Rotate User-Agents** (Chrome 129-131)
4. **Human delays**: `random.uniform(3.0, 5.0)` seconds between actions
5. **Manual submit default**: Let user click "Create" button (avoid bot detection)

**Usage Pattern:**
```python
from src.utils.stealth_driver import create_stealth_driver, add_human_delays

driver = create_stealth_driver(profile_path, headless=False)
# Fill form...
time.sleep(add_human_delays())  # 3-5s random delay
# Next action...
```

---

## Queue Workflows

### State Machine

```
pending → running → completed
   ↓         ↓          ↑
   ↓      paused    ────┘
   ↓         ↓
   └──→ cancelled
```

**Rules:**
- Never skip states (e.g., pending → completed directly)
- Save state after EVERY transition
- Progress tracked: `songs_completed / total_songs`

### Queue Persistence

```python
# queue_manager.py pattern
def add_queue_entry(self, account_name: str, song_count: int, batch_size: int, prompts: List[SunoPrompt]) -> str:
    """
    Validation order:
    1. prompts available >= song_count
    2. batch_size in [1, 10]
    3. account exists in AccountManager
    4. No duplicate queue_id
    
    Then:
    1. Create QueueEntry
    2. Add to self.queues dict
    3. self._save_state() ← CRITICAL: Immediate save!
    4. Update prompt_cursor
    5. Return queue_id
    """
    # Validation...
    entry = QueueEntry(...)
    self.queues[queue_id] = entry
    self._save_state()  # Atomic write to queue_state.json
    return queue_id

def _save_state(self):
    """
    Always use atomic write:
    1. Write to temp file
    2. Rename to replace original
    3. Prevents corruption on crash
    """
    atomic_write_json(QUEUE_STATE_FILE, {
        "version": "1.0",
        "prompts": [p.to_dict() for p in self.prompts],
        "prompt_cursor": self.prompt_cursor,
        "queues": [q.to_dict() for q in self.queues.values()]
    })
```

### Batch Execution Engine

See `batch_song_creator.py` for full implementation. Key patterns:

```python
def execute_queues(self, queues: List[QueueEntry], progress_callback: Callable):
    """
    For each queue:
      1. Split into batches (e.g., 30 songs, batch_size=5 → 6 batches)
      2. For each batch:
         a. Open Chrome with profile
         b. Create N tabs (N = batch_size)
         c. For each tab:
            - Fill form with 3-5s delays
            - Wait for user to click Create (or auto-click)
            - Extract song URLs
            - Save to history
            - Update queue progress
            - Call progress_callback(queue_id, batch, song, "success", msg)
         d. Close tabs after 10 songs (memory cleanup)
      3. Mark queue completed
      4. Save state
    
    Error handling:
    - If 1 song fails → log error, continue with rest
    - If browser crashes → mark queue failed, save state
    - Always call progress_callback with status
    """
```

**Progress Callback Signature** (DO NOT change):
```python
def callback(
    queue_id: str,
    batch_num: int,
    song_num: int,
    status: str,  # "creating" | "success" | "error"
    message: str
) -> None:
    pass
```

---

## API Integration

### Suno API Client

```python
# suno_api_client.py pattern
class SunoApiClient:
    def __init__(self, session_token: str):
        """
        Always require session_token in constructor.
        Never store profiles or launch browsers here.
        """
        self.token = session_token
        self.headers = {
            "Authorization": f"Bearer {session_token}",
            "Content-Type": "application/json"
        }
    
    def fetch_clips(self, page: int = 0) -> List[dict]:
        """
        Paginated API: /api/feed/v2?page=N
        Returns 20 clips per page.
        
        Handle:
        - 401 Unauthorized → raise SessionTokenError
        - 429 Rate limit → retry with exponential backoff
        - Network errors → retry RETRY_ATTEMPTS times
        """
        url = f"{SUNO_API_URL}/feed/v2"
        response = requests.get(url, headers=self.headers, params={"page": page})
        response.raise_for_status()
        return response.json()
```

### Form Automation

React controlled inputs require special handling:

```python
# suno_form_automation.py pattern
class SunoFormFiller:
    def fill_lyrics(self, driver: webdriver.Chrome, lyrics: str):
        """
        React inputs ignore send_keys()!
        Use native setter + synthetic events:
        """
        lyrics_input = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='lyrics']")
        driver.execute_script("""
            const input = arguments[0];
            const value = arguments[1];
            
            // Get native setter
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value'
            ).set;
            
            // Call native setter (bypasses React)
            nativeSetter.call(input, value);
            
            // Dispatch events React listens for
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, lyrics_input, lyrics)
        
        time.sleep(add_human_delays())  # 3-5s delay
```

---

## Browser Automation

### Profile Lock Error

**Problem**: Chrome crashes with "Chrome instance exited" if profile already in use.

```python
# session_manager.py pattern
def launch_browser(self, account_name: str) -> Optional[webdriver.Chrome]:
    try:
        driver = create_stealth_driver(profile_path, headless=False)
        return driver
    except Exception as e:
        if "Chrome instance exited" in str(e):
            # Profile locked by another Chrome window
            logger.error(f"Profile {account_name} is locked")
            # UI should show: "Đóng tất cả cửa sổ Chrome và thử lại"
            return None
        raise
```

**Fix**: Close ALL Chrome windows before launching with same profile.

### Tab Management

```python
# batch_song_creator.py pattern
def create_batch_tabs(self, driver: webdriver.Chrome, batch_size: int):
    """
    Memory optimization:
    - Close tabs after every 10 songs
    - Reopen fresh tabs for next batch
    - Prevents Chrome memory bloat (5GB+ after 50 tabs)
    """
    tabs = []
    for i in range(batch_size):
        if i == 0:
            tabs.append(driver.current_window_handle)
        else:
            driver.execute_script("window.open('');")
            tabs.append(driver.window_handles[-1])
    return tabs
```

---

## Data Models

Models live in `src/models/data_models.py` but documented here for context.

### Account Model

```python
@dataclass
class Account:
    name: str
    email: str
    created_at: str
    last_used: str
    status: str = "active"
    
    # JSON pattern: name is KEY, not in value
    # See config/AGENTS.md#json-persistence
```

### QueueEntry Model

```python
@dataclass
class QueueEntry:
    id: str
    account_name: str
    total_songs: int
    batch_size: int
    songs_completed: int = 0
    status: str = "pending"  # pending|running|paused|completed|failed|cancelled
    progress_percent: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    current_batch: int = 0
```

---

## Logging

Use shared Logger singleton:

```python
from src.utils.logger import logger

class YourManager:
    def some_method(self):
        logger.info("Operation started")
        try:
            # Work...
            logger.debug(f"Processed {count} items")
        except Exception as e:
            logger.error(f"Operation failed: {e}", exc_info=True)
```

**Log Levels:**
- `DEBUG`: Verbose details (API responses, state dumps)
- `INFO`: Normal flow (queue started, download completed)
- `WARNING`: Recoverable issues (retry after timeout)
- `ERROR`: Failures requiring attention (session expired, validation failed)

Logs write to `logs/app_YYYYMMDD.log`.

---

## Prompt Templates

XML templates in `src/prompt/` folder (e.g., `default-prompt.xml`):

```xml
<PROMPTS>
  <PROMPT>
    <TITLE>Song Title</TITLE>
    <LYRICS>
Verse 1 lyrics...
Chorus...
    </LYRICS>
    <STYLE>Pop, upbeat, 80s</STYLE>
  </PROMPT>
</PROMPTS>
```

**Parsing:** Use `SunoPromptParser` from `src/utils/prompt_parser.py`.

```python
from src.utils.prompt_parser import SunoPromptParser

parser = SunoPromptParser()
prompts = parser.parse_file("prompts/my-batch.xml")  # Returns List[SunoPrompt]
```

---

## Testing Patterns

Mock managers in tests:

```python
from unittest.mock import MagicMock, patch

@patch('src.core.batch_song_creator.webdriver.Chrome')
def test_song_creation(mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    
    # Test without launching real browser
    creator = BatchSongCreator(session_manager=mock_session, queue_manager=mock_queue)
    creator.execute_queues([queue], callback=lambda *args: None)
    
    assert mock_driver.get.called
```

See `tests/AGENTS.md#mocking-patterns` for comprehensive guide.

---

## Entry Points

| File | Primary Class/Function | Purpose |
|------|----------------------|---------|
| `account_manager.py` | `AccountManager` | Account CRUD, JSON persistence |
| `session_manager.py` | `SessionManager` | Chrome launch, token extraction |
| `queue_manager.py` | `QueueManager` | Queue CRUD, state persistence |
| `batch_song_creator.py` | `BatchSongCreator` | Multi-queue execution engine |
| `download_manager.py` | `DownloadManager` | Download orchestration |
| `song_creation_history_manager.py` | `SongCreationHistoryManager` | History tracking, CSV export |
| `suno_api_client.py` | `SunoApiClient` | API wrapper |
| `suno_form_automation.py` | `SunoFormFiller`, `SunoPersonaSelector`, `SunoModeSelector`, `SunoAdvancedOptionsConfigurator` | Form automation helpers |

---

## Cross-References

- **UI integration**: See `src/ui/AGENTS.md#panel-patterns`
- **Configuration**: See `config/AGENTS.md#path-constants`
- **Testing**: See `tests/AGENTS.md#mocking-patterns`
- **Architecture diagrams**: See `memory-bank/FLOW_DIAGRAMS.md#system-architecture`

---

**Questions?** Check root `AGENTS.md` for general guidelines or Memory Bank for design rationale.
