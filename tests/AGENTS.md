# AGENTS.md

**Audience:** AI coding agents, developers writing tests  
**Applies to:** `tests/**/*.py`  
**Scope:** Test structure, mocking patterns, fixture conventions  
**Last reviewed:** 2025-11-10  
**Owners:** Core team, QA

---

## Test Structure

### File Naming

```
tests/
├── test_account_manager.py      # Unit test for AccountManager
├── test_queue_manager.py        # Unit test for QueueManager
├── test_batch_song_creator.py   # Unit test for BatchSongCreator
├── test_queue_workflow.py       # Integration test (end-to-end queue flow)
├── test_queue_stress.py         # Stress test (100+ songs)
├── test_utils.py                # Unit tests for utils
├── fixtures/                    # Shared test data
│   ├── test_prompts.xml
│   └── mock_responses.json
└── conftest.py                  # Pytest fixtures
```

**Conventions**:
- Unit tests: `test_<module>.py` (e.g., `test_queue_manager.py`)
- Integration tests: `test_<feature>_workflow.py` (e.g., `test_queue_workflow.py`)
- Stress tests: `test_<feature>_stress.py` (e.g., `test_queue_stress.py`)

### Test Function Naming

```python
def test_<function>_<scenario>_<expected>():
    """
    Pattern: test_what_when_then
    """
    pass

# Examples
def test_add_queue_valid_inputs_returns_queue_id():
    """Test QueueManager.add_queue_entry() with valid inputs returns queue ID"""
    pass

def test_add_queue_duplicate_id_raises_error():
    """Test QueueManager.add_queue_entry() with duplicate ID raises QueueValidationError"""
    pass

def test_batch_creator_handles_browser_crash_gracefully():
    """Test BatchSongCreator recovers from browser crash"""
    pass
```

---

## Mocking Patterns

### Mock Selenium WebDriver

**Problem**: Don't want to launch real Chrome in tests.

```python
from unittest.mock import MagicMock, patch

@patch('src.core.batch_song_creator.webdriver.Chrome')
def test_batch_creator_opens_browser(mock_chrome):
    """Test that BatchSongCreator opens Chrome with correct profile"""
    # Arrange
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    
    creator = BatchSongCreator(...)
    
    # Act
    creator.execute_queues([queue], callback=lambda *args: None)
    
    # Assert
    mock_chrome.assert_called_once()
    assert '--user-data-dir' in str(mock_chrome.call_args)
    mock_driver.get.assert_called()  # Navigated somewhere
```

### Mock API Calls

**Problem**: Don't want to hit real Suno API in tests.

```python
import pytest
from unittest.mock import patch, MagicMock

@patch('src.core.suno_api_client.requests.get')
def test_api_client_fetches_clips(mock_get):
    """Test SunoApiClient.fetch_clips() parses API response"""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": "abc123", "title": "Test Song", "audio_url": "https://..."}
    ]
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    client = SunoApiClient(session_token="fake_token")
    
    # Act
    clips = client.fetch_clips(page=0)
    
    # Assert
    assert len(clips) == 1
    assert clips[0]["id"] == "abc123"
    mock_get.assert_called_once_with(
        "https://studio-api.prod.suno.com/api/feed/v2",
        headers={"Authorization": "Bearer fake_token"},
        params={"page": 0}
    )
```

### Mock File I/O

**Problem**: Don't want to read/write real files in tests.

```python
from unittest.mock import patch, mock_open

@patch('builtins.open', new_callable=mock_open, read_data='{"account1": {"email": "test@example.com"}}')
@patch('pathlib.Path.exists', return_value=True)
def test_account_manager_loads_accounts(mock_exists, mock_file):
    """Test AccountManager loads accounts from JSON"""
    # Arrange
    manager = AccountManager()
    
    # Act
    manager.load_accounts()
    
    # Assert
    assert "account1" in manager.accounts
    assert manager.accounts["account1"].email == "test@example.com"
    mock_file.assert_called()
```

### Mock Progress Callbacks

**Pattern**: Test that callbacks are invoked correctly.

```python
def test_download_manager_calls_progress_callback():
    """Test DownloadManager invokes progress_callback during download"""
    # Arrange
    callback_mock = MagicMock()
    manager = DownloadManager()
    clips = [
        MagicMock(id="1", title="Song 1"),
        MagicMock(id="2", title="Song 2")
    ]
    
    # Act
    with patch.object(manager, '_download_clip'):  # Skip actual download
        manager.batch_download(clips, progress_callback=callback_mock)
    
    # Assert
    assert callback_mock.call_count == 2  # Called for each clip
    callback_mock.assert_any_call("Downloading Song 1", 50)
    callback_mock.assert_any_call("Downloading Song 2", 100)
```

---

## Fixture Conventions

### Conftest.py

Shared fixtures in `tests/conftest.py`:

```python
import pytest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock

@pytest.fixture
def temp_dir():
    """Provides temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_account_manager():
    """Provides mock AccountManager with default accounts"""
    mock = MagicMock()
    mock.get_all_accounts.return_value = {
        "test_account": MagicMock(name="test_account", email="test@example.com")
    }
    mock.account_exists.return_value = False  # Default: no duplicates
    return mock

@pytest.fixture
def mock_session_manager():
    """Provides mock SessionManager"""
    mock = MagicMock()
    mock.get_session_token_from_me_page.return_value = ("fake_token", MagicMock())
    return mock

@pytest.fixture
def sample_prompts():
    """Provides sample SunoPrompt list for testing"""
    from src.utils.prompt_parser import SunoPrompt
    return [
        SunoPrompt(title="Song 1", lyrics="Verse 1...", style="Pop"),
        SunoPrompt(title="Song 2", lyrics="Verse 2...", style="Rock"),
        SunoPrompt(title="Song 3", lyrics="Verse 3...", style="Jazz")
    ]

@pytest.fixture
def mock_config(monkeypatch, temp_dir):
    """Patches config.settings to use temp directories"""
    monkeypatch.setattr('config.settings.BASE_DIR', temp_dir)
    monkeypatch.setattr('config.settings.PROFILES_DIR', temp_dir / 'profiles')
    monkeypatch.setattr('config.settings.DATA_DIR', temp_dir / 'data')
    monkeypatch.setattr('config.settings.ACCOUNTS_FILE', temp_dir / 'data' / 'accounts.json')
    monkeypatch.setattr('config.settings.QUEUE_STATE_FILE', temp_dir / 'data' / 'queue_state.json')
    
    # Create directories
    (temp_dir / 'profiles').mkdir()
    (temp_dir / 'data').mkdir()
    
    yield temp_dir
```

### Fixture Usage

```python
def test_queue_manager_with_fixtures(mock_account_manager, sample_prompts, mock_config):
    """Test QueueManager.add_queue_entry() with fixtures"""
    # Arrange
    manager = QueueManager()
    manager.account_manager = mock_account_manager
    manager.prompts = sample_prompts
    
    # Act
    queue_id = manager.add_queue_entry(
        account_name="test_account",
        song_count=3,
        batch_size=1,
        prompts=sample_prompts
    )
    
    # Assert
    assert queue_id is not None
    assert len(manager.queues) == 1
```

---

## Integration Testing

### End-to-End Queue Workflow

```python
# tests/test_queue_workflow.py
import pytest
from unittest.mock import patch, MagicMock

@patch('src.core.batch_song_creator.webdriver.Chrome')
@patch('src.core.suno_api_client.requests.get')
def test_full_queue_workflow_e2e(mock_api, mock_chrome, mock_config, sample_prompts):
    """
    Integration test: Add queue → Start → Complete → History persisted
    Mocks: Browser, API
    Real: QueueManager, BatchSongCreator, state persistence
    """
    # Arrange: Set up managers
    from src.core.account_manager import AccountManager
    from src.core.queue_manager import QueueManager
    from src.core.batch_song_creator import BatchSongCreator
    from src.core.song_creation_history_manager import SongCreationHistoryManager
    
    account_manager = AccountManager()
    account_manager.accounts = {"test_account": MagicMock(name="test_account")}
    
    queue_manager = QueueManager()
    queue_manager.prompts = sample_prompts
    
    history_manager = SongCreationHistoryManager()
    
    # Mock browser
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    
    # Mock API
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "song123", "audio_url": "https://..."}]
    mock_api.return_value = mock_response
    
    # Act: Add queue
    queue_id = queue_manager.add_queue_entry(
        account_name="test_account",
        song_count=3,
        batch_size=1,
        prompts=sample_prompts
    )
    
    # Act: Execute queue
    creator = BatchSongCreator(
        session_manager=MagicMock(),
        queue_manager=queue_manager,
        history_manager=history_manager
    )
    
    results = creator.execute_queues(
        queues=[queue_manager.queues[queue_id]],
        callback=lambda *args: None  # Ignore progress
    )
    
    # Assert: Queue completed
    assert queue_manager.queues[queue_id].status == "completed"
    assert queue_manager.queues[queue_id].songs_completed == 3
    
    # Assert: History recorded
    assert len(history_manager.history) == 3
    
    # Assert: State persisted (check JSON file exists)
    import json
    from config.settings import QUEUE_STATE_FILE
    assert QUEUE_STATE_FILE.exists()
    with open(QUEUE_STATE_FILE) as f:
        state = json.load(f)
        assert len(state["queues"]) == 1
        assert state["queues"][0]["status"] == "completed"
```

---

## Stress Testing

### High-Volume Queue Test

```python
# tests/test_queue_stress.py
@patch('src.core.batch_song_creator.webdriver.Chrome')
def test_queue_handles_100_songs_without_memory_leak(mock_chrome, mock_config):
    """Stress test: 100 songs in queue, verify no memory leak"""
    # Arrange
    from src.utils.prompt_parser import SunoPrompt
    prompts = [
        SunoPrompt(title=f"Song {i}", lyrics=f"Lyrics {i}", style="Pop")
        for i in range(100)
    ]
    
    queue_manager = QueueManager()
    queue_manager.prompts = prompts
    
    # Mock browser (lightweight)
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    
    # Act
    queue_id = queue_manager.add_queue_entry(
        account_name="test_account",
        song_count=100,
        batch_size=10,
        prompts=prompts
    )
    
    creator = BatchSongCreator(...)
    creator.execute_queues([queue_manager.queues[queue_id]], callback=lambda *args: None)
    
    # Assert: Completed without crash
    assert queue_manager.queues[queue_id].status == "completed"
    assert queue_manager.queues[queue_id].songs_completed == 100
    
    # Check memory (basic)
    import gc
    gc.collect()
    # Verify no lingering Chrome processes (in real test, check with psutil)
```

---

## UI Testing

### Mock CustomTkinter Widgets

**Problem**: Don't want to render actual GUI in tests.

```python
from unittest.mock import MagicMock, patch

@patch('src.ui.account_panel.ctk.CTkFrame')
@patch('src.ui.account_panel.ctk.CTkButton')
def test_account_panel_add_validation(mock_button, mock_frame):
    """Test AccountPanel.add_account() validates duplicate names"""
    # Arrange
    mock_account_manager = MagicMock()
    mock_account_manager.account_exists.return_value = True  # Duplicate
    
    panel = AccountPanel(
        parent=MagicMock(),
        account_manager=mock_account_manager,
        session_manager=MagicMock()
    )
    
    # Act & Assert
    with patch('tkinter.messagebox.showerror') as mock_error:
        panel.add_account_with_name("duplicate_name")
        mock_error.assert_called_once_with("Lỗi", "Tên tài khoản đã tồn tại")
```

### Test Logic, Not Rendering

**Best practice**: Test business logic in panels, not actual rendering.

```python
def test_download_panel_validation():
    """Test DownloadPanel validates inputs before download"""
    # Mock dependencies
    mock_download_manager = MagicMock()
    
    panel = DownloadPanel(
        parent=MagicMock(),
        download_manager=mock_download_manager,
        session_manager=MagicMock()
    )
    
    # Simulate empty account selection
    panel.account_var = MagicMock()
    panel.account_var.get.return_value = ""
    
    # Mock messagebox
    with patch('tkinter.messagebox.showerror') as mock_error:
        panel.start_download()
        
        # Assert: Error shown, download not started
        mock_error.assert_called_once()
        mock_download_manager.fetch_clips.assert_not_called()
```

---

## CLI Testing

### Subprocess Tests

```python
import subprocess
import pytest

def test_batch_download_cli_help():
    """Test CLI --help flag works"""
    result = subprocess.run(
        ["python", "legacy_modules/suno_batch_download.py", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "--profile" in result.stdout

def test_batch_download_cli_missing_args():
    """Test CLI fails gracefully with missing required args"""
    result = subprocess.run(
        ["python", "legacy_modules/suno_batch_download.py"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode != 0
    assert "error:" in result.stderr.lower()
```

---

## Performance Testing

### Timing Assertions

```python
import time

def test_queue_manager_save_state_is_fast():
    """Test QueueManager._save_state() completes in <100ms"""
    manager = QueueManager()
    manager.queues = {f"q{i}": MagicMock() for i in range(10)}  # 10 queues
    
    start = time.time()
    manager._save_state()
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # Less than 100ms
```

---

## Coverage Guidelines

### Target Coverage

- **Core layer**: 80%+ (business logic critical)
- **UI layer**: 50%+ (test logic, not rendering)
- **Utils layer**: 70%+ (pure functions, easy to test)
- **Models layer**: 90%+ (dataclasses, simple)

### Run Coverage

```bash
# Install coverage tool
pip install pytest-cov

# Run with coverage
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

---

## Common Pitfalls

### ❌ Real Browser in Tests

```python
# WRONG: Launches real Chrome (slow, flaky)
def test_session_manager():
    manager = SessionManager()
    token, driver = manager.get_session_token_from_me_page("account")
    driver.quit()
```

```python
# CORRECT: Mock webdriver
@patch('src.core.session_manager.webdriver.Chrome')
def test_session_manager(mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    
    manager = SessionManager()
    # Test logic without real browser
```

### ❌ Real File I/O

```python
# WRONG: Writes to real filesystem
def test_account_manager_save():
    manager = AccountManager()
    manager.save_accounts()  # Writes to data/suno_accounts.json
```

```python
# CORRECT: Mock or use temp directory
def test_account_manager_save(mock_config):  # Uses temp_dir fixture
    manager = AccountManager()
    manager.save_accounts()  # Writes to /tmp/.../accounts.json
```

### ❌ Timeout-Dependent Tests

```python
# WRONG: Flaky on slow CI
def test_download_completes_fast():
    start = time.time()
    download_clips([...])
    assert time.time() - start < 5.0  # May fail on slow CI
```

```python
# CORRECT: Mock slow operations
@patch('requests.get')
def test_download_logic(mock_get):
    mock_get.return_value = MagicMock(content=b"fake_mp3_data")
    # Test logic, not actual download speed
```

---

## Entry Points

| File | Purpose | Key Tests |
|------|---------|-----------|
| `test_account_manager.py` | Account CRUD | Load, save, validation |
| `test_queue_manager.py` | Queue CRUD | Add, update, state persistence |
| `test_batch_song_creator.py` | Batch execution | Browser launch, form fill, error handling |
| `test_queue_workflow.py` | Integration | End-to-end queue flow |
| `test_queue_stress.py` | Stress | High-volume operations |
| `test_utils.py` | Utilities | Helper functions |
| `conftest.py` | Fixtures | Shared test setup |

---

## Cross-References

- **Mocking Core**: See `src/core/AGENTS.md#manager-lifecycle` for manager patterns
- **Mocking UI**: See `src/ui/AGENTS.md#threading-model` for UI callback patterns
- **Config Mocking**: See `config/AGENTS.md#configuration-testing` for path mocking
- **CLI Testing**: See `legacy_modules/AGENTS.md#testing-legacy-modules` for CLI tests

---

**Questions?** Check root `AGENTS.md` for test running commands.
