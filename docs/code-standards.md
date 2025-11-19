# Code Standards và Conventions

**Phiên Bản Tài Liệu:** 2.0
**Ngày Cập Nhật:** 18/11/2025
**Áp Dụng:** Mọi đóng góp code mới

## Tổng Quan

Document này định nghĩa các tiêu chuẩn coding, conventions, và best practices cho Suno Account Manager v2.0. Mục tiêu là đảm bảo tính consistency, maintainability, và quality của codebase.

## Language và Framework Standards

### Python Version và Features
- **Python Version**: 3.10+ (yêu cầu tối thiểu)
- **Type Hints**: Bắt buộc cho public APIs, khuyến khích cho internal code
- **Dataclasses**: Ưu tiên sử dụng cho data models
- **Pathlib**: Bắt buộc cho file path operations
- **f-strings**: Bắt buộc cho string formatting

### Framework Standards
- **GUI Framework**: CustomTkinter (không dùng tkinter gốc)
- **Browser Automation**: Selenium WebDriver với StealthDriver
- **Testing**: pytest với unittest.mock
- **Logging**: Custom logger singleton (không dùng logging module trực tiếp)

### Import Standards

#### Import Order (PEP 8)
```python
# 1. Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict

# 2. Third-party imports
import customtkinter as ctk
import pytest
from selenium import webdriver

# 3. Local imports
from config.settings import APP_NAME
from src.core.account_manager import AccountManager
from src.utils import logger
```

#### Import Best Practices
- **Sử dụng explicit imports**: Tránh `from module import *`
- **Relative imports**: Cho internal modules (`from . import helper`)
- **Alias convention**: `import customtkinter as ctk`
- **Type imports**: Sử dụng `from typing import` cho type hints

## Code Style và Formatting

### PEP 8 Compliance
- **Line Length**: Maximum 120 characters (không phải 79)
- **Indentation**: 4 spaces (không dùng tabs)
- **Blank Lines**: 2 blank lines trước class/function, 1 blank lines logic sections
- **Naming**: snake_case cho variables/functions, PascalCase cho classes

### Example Code Style
```python
"""
Session Manager - Manages Chrome sessions and authentication tokens
"""
import time
from pathlib import Path
from typing import Optional

from config.settings import PROFILES_DIR, SUNO_URL
from src.utils import logger


class SessionManager:
    """Manages Chrome sessions and authentication tokens"""

    def __init__(self, profile_timeout: int = 300):
        self.profile_timeout = profile_timeout
        self._active_sessions: Dict[str, webdriver.Chrome] = {}

    def get_session_token(self, account_name: str) -> Optional[str]:
        """
        Extract session token from Chrome profile.

        Args:
            account_name: Name of the account

        Returns:
            Session token string if found, None otherwise

        Raises:
            SessionError: If profile access fails
        """
        profile_path = PROFILES_DIR / account_name

        if not profile_path.exists():
            logger.warning(f"Profile not found: {account_name}")
            return None

        try:
            return self._extract_token_from_profile(profile_path)
        except Exception as e:
            logger.error(f"Failed to extract token from {account_name}: {e}")
            return None

    def _extract_token_from_profile(self, profile_path: Path) -> str:
        """Internal method to extract token from Chrome profile."""
        # Implementation details
        pass
```

### Comment và Documentation Standards

#### Docstring Format (Google Style)
```python
def create_batch_songs(
    prompts: List[SunoPrompt],
    account_name: str,
    batch_size: int = 5,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[SongCreationRecord]:
    """Create multiple songs in batches using Chrome automation.

    This function orchestrates the creation of multiple songs by opening
    multiple Chrome tabs, filling forms, and submitting them to Suno.com.

    Args:
        prompts: List of parsed song prompts with title, lyrics, and style
        account_name: Account name to use for creation
        batch_size: Number of tabs to open concurrently (1-10)
        progress_callback: Optional callback for progress updates

    Returns:
        List of creation records with metadata and results

    Raises:
        ValueError: If prompts list is empty or invalid batch_size
        SessionError: If account session is invalid or expired
        ChromeDriverError: If browser automation fails

    Example:
        >>> prompts = [SunoPrompt("Song 1", "Lyrics", "Pop")]
        >>> results = create_batch_songs(prompts, "my_account", batch_size=3)
        >>> print(f"Created {len(results)} songs")
    """
```

#### Comment Standards
- **Inline Comments**: Giải thích business logic phức tạp
- **TODO Comments**: Format `TODO: Description - Owner YYYY-MM-DD`
- **FIXME Comments**: Format `FIXME: Critical issue - Owner YYYY-MM-DD`
- **Vietnamese Comments**: Cho business logic, English cho technical details

## File Organization và Structure

### Directory Structure Standards
```
src/
├── ui/                    # Presentation Layer (UI components)
│   ├── components/        # Reusable UI widgets
│   └── panels/           # Main UI panels
├── core/                  # Application/Business Logic
├── models/                # Domain models and dataclasses
├── utils/                 # Infrastructure utilities
└── __init__.py           # Package initialization
```

### File Naming Conventions
- **Modules**: `snake_case.py` (ví dụ: `account_manager.py`)
- **Classes**: `PascalCase` (ví dụ: `AccountManager`)
- **Functions/Variables**: `snake_case` (ví dụ: `get_session_token`)
- **Constants**: `UPPER_SNAKE_CASE` (ví dụ: `MAX_RETRY_ATTEMPTS`)
- **Private**: Prefix `_` (ví dụ: `_internal_method`)

### Module Structure Template
```python
"""
Module description - one sentence summary.

Detailed description of module purpose and responsibilities.
"""

# Standard library imports
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Third-party imports
import customtkinter as ctk
import requests
from selenium import webdriver

# Local imports
from config.settings import BASE_DIR
from src.models.data_models import Account
from src.utils import logger

# Module constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Exception classes
class ModuleError(Exception):
    """Base exception for this module."""
    pass

class SpecificError(ModuleError):
    """Specific error with detailed context."""
    pass

# Main class/function implementations
class ClassName:
    """Class description following docstring format."""

    def __init__(self, param1: str, param2: Optional[int] = None):
        self.param1 = param1
        self.param2 = param2 or DEFAULT_TIMEOUT

    def method_name(self, data: Dict[str, Any]) -> bool:
        """Method description with args and returns."""
        return True

# Export definitions
__all__ = [
    "ClassName",
    "ModuleError",
    "SpecificError",
]
```

## Architecture Patterns và Principles

### Clean Architecture Adherence

#### Layer Dependencies
```
UI Layer (src/ui/)
    ↓ depends on
Core Layer (src/core/)
    ↓ depends on
Models Layer (src/models/)
    ↓ uses
Utils Layer (src/utils/)
```

**Anti-Pattern Examples:**
```python
# ❌ WRONG: UI accessing utils directly
from src.utils.stealth_driver import create_stealth_driver  # Don't do this

# ❌ WRONG: Core accessing UI
from src.ui.main_window import MainWindow  # Don't do this

# ✅ CORRECT: UI using core managers
from src.core.session_manager import SessionManager
```

#### Dependency Injection Pattern
```python
class AccountPanel(ctk.CTkFrame):
    """Account management UI panel with dependency injection."""

    def __init__(
        self,
        parent: ctk.CTk,
        account_manager: AccountManager,
        session_manager: SessionManager
    ):
        super().__init__(parent)
        self.account_manager = account_manager  # Injected dependency
        self.session_manager = session_manager  # Injected dependency
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        # UI implementation using injected managers
        pass
```

### Design Patterns Usage

#### Singleton Pattern (Logger)
```python
class Logger:
    """Application logger singleton."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize logger instance."""
        self.logger = logging.getLogger("SunoApp")
        # Setup configuration
```

#### Factory Pattern (Driver Creation)
```python
class StealthDriverFactory:
    """Factory for creating anti-detection Chrome drivers."""

    @staticmethod
    def create_driver(
        profile_path: Path,
        headless: bool = False,
        user_agent: Optional[str] = None
    ) -> webdriver.Chrome:
        """Create configured Chrome driver with anti-detection."""
        # Factory implementation
        pass
```

## Type System và Data Modeling

### Type Hints Standards
```python
from typing import (
    Optional, List, Dict, Any, Tuple, Union,
    Callable, Protocol, TypeAlias, Generic
)

# Type aliases for complex types
SongId: TypeAlias = str
ProgressCallback: TypeAlias = Callable[[int, int], None]

# Protocol for interfaces
class Downloadable(Protocol):
    """Protocol for items that can be downloaded."""

    def get_download_url(self) -> str:
        """Return download URL for the item."""
        ...

# Generic classes
class DataManager(Generic[T]):
    """Generic data manager with type safety."""

    def __init__(self) -> None:
        self._items: List[T] = []

    def add_item(self, item: T) -> None:
        """Add typed item to collection."""
        self._items.append(item)
```

### Dataclass Standards
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class SongCreationRecord:
    """Record of a generated song with full metadata."""

    # Required fields
    song_id: str
    title: str
    prompt_index: int
    account_name: str
    status: str

    # Optional fields with defaults
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_successful(self) -> bool:
        """Check if song creation was successful."""
        return self.status == "completed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
```

## Error Handling và Logging

### Exception Hierarchy
```python
# Base application exception
class SunoAppError(Exception):
    """Base exception for Suno Account Manager."""
    pass

# Specific exception categories
class AuthenticationError(SunoAppError):
    """Authentication and session related errors."""
    pass

class SessionExpiredError(AuthenticationError):
    """Session token has expired."""
    pass

class BrowserAutomationError(SunoAppError):
    """Chrome automation related errors."""
    pass

class QueueValidationError(SunoAppError):
    """Queue management validation errors."""
    pass
```

### Error Handling Patterns
```python
def risky_operation(data: Dict[str, Any]) -> Result:
    """Example of comprehensive error handling."""
    try:
        # Validate input
        if not data or "required_field" not in data:
            raise ValueError("Missing required field in data")

        # Perform operation
        result = _perform_operation(data)

        # Validate result
        if not result.is_valid():
            raise OperationError(f"Invalid result: {result.errors}")

        logger.info(f"Operation completed successfully: {result.id}")
        return result

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        # Trigger re-authentication flow
        self._handle_auth_error(e)
        raise

    except Exception as e:
        logger.error(f"Unexpected error in risky_operation: {e}", exc_info=True)
        # Clean up resources
        self._cleanup()
        raise OperationError(f"Operation failed: {e}") from e
```

### Logging Standards
```python
from src.utils import logger

# Use appropriate log levels
logger.debug("Detailed debug information: variable=%s", variable)
logger.info("Normal operation completed: processed %d items", count)
logger.warning("Potential issue detected: retry attempt %d/%d", attempt, max_attempts)
logger.error("Operation failed: error=%s", str(error))

# Structured logging with context
logger.info(
    "Queue operation completed",
    extra={
        "queue_id": queue.id,
        "account_name": queue.account_name,
        "songs_processed": queue.completed_count,
        "duration_seconds": elapsed_time
    }
)

# Error logging with exception details
logger.error(
    "Failed to create song",
    exc_info=True,
    extra={
        "song_title": song.title,
        "account_name": account_name,
        "prompt_index": prompt_index
    }
)
```

## Testing Standards

### Test Structure và Naming
```python
# File naming: test_<module_name>.py
# Class naming: Test<ClassName>
# Method naming: test_<scenario>_<expected_result>

import pytest
from unittest.mock import Mock, patch
from src.core.queue_manager import QueueManager, QueueValidationError

class TestQueueManager:
    """Test suite for QueueManager functionality."""

    @pytest.fixture
    def queue_manager(self, tmp_path):
        """Create QueueManager instance for testing."""
        state_file = tmp_path / "test_queue_state.json"
        return QueueManager(state_file=state_file)

    @pytest.fixture
    def sample_prompts(self):
        """Sample prompts for testing."""
        return [
            SunoPrompt("Song 1", "Lyrics 1", "Pop"),
            SunoPrompt("Song 2", "Lyrics 2", "Rock"),
        ]

    def test_add_queue_entry_success(self, queue_manager, sample_prompts):
        """Test successful queue entry addition."""
        # Arrange
        queue_manager.load_prompts(sample_prompts)

        # Act
        entry = queue_manager.add_queue_entry(
            account_name="test_account",
            total_songs=2,
            songs_per_batch=1
        )

        # Assert
        assert entry is not None
        assert entry.account_name == "test_account"
        assert entry.total_songs == 2
        assert entry.status == "pending"

    def test_add_queue_entry_exceeds_prompts_raises_error(self, queue_manager):
        """Test that adding queue exceeding prompts raises validation error."""
        # Arrange
        queue_manager.load_prompts([SunoPrompt("Song", "Lyrics", "Pop")])

        # Act & Assert
        with pytest.raises(QueueValidationError) as exc_info:
            queue_manager.add_queue_entry(
                account_name="test_account",
                total_songs=5,  # Exceeds available prompts (1)
                songs_per_batch=1
            )

        assert "Insufficient prompts" in str(exc_info.value)
```

### Test Coverage Requirements
- **Unit Tests**: Minimum 80% coverage cho core business logic
- **Integration Tests**: Critical user workflows
- **Mock Strategy**: Mock external dependencies (Selenium, API calls)
- **Test Data**: Use fixtures cho repeatable test data

## Security Best Practices

### Input Validation
```python
def validate_prompt_input(title: str, lyrics: str, style: str) -> bool:
    """Validate user input for song creation prompts."""

    # Length validation
    if not (10 <= len(title) <= 100):
        raise ValueError("Title must be between 10 and 100 characters")

    if not (50 <= len(lyrics) <= 2000):
        raise ValueError("Lyrics must be between 50 and 2000 characters")

    # Content validation
    if any(char in title for char in ['<', '>', '"', "'"]):
        raise ValueError("Title contains invalid characters")

    # Sanitization
    style = sanitize_style_input(style)

    return True

def sanitize_style_input(style: str) -> str:
    """Sanitize style input to prevent injection."""
    # Remove potential dangerous characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ,.-0123456789")
    return ''.join(char for char in style if char in allowed_chars)
```

### Session Management Security
```python
class SecureSessionManager:
    """Secure session management with token protection."""

    def __init__(self):
        self._tokens: Dict[str, str] = {}
        self._token_expiry: Dict[str, datetime] = {}

    def store_token(self, account_name: str, token: str) -> None:
        """Store session token with expiry."""
        # Validate token format (JWT)
        if not self._is_valid_jwt(token):
            raise ValueError("Invalid session token format")

        # Set expiry (24 hours from now)
        expiry = datetime.now() + timedelta(hours=24)

        self._tokens[account_name] = token
        self._token_expiry[account_name] = expiry

        # Log token storage (masked for security)
        masked_token = self._mask_token(token)
        logger.info(f"Session token stored for {account_name}: {masked_token}")

    def _mask_token(self, token: str) -> str:
        """Mask token for logging purposes."""
        if len(token) <= 8:
            return "*" * len(token)
        return token[:4] + "*" * (len(token) - 8) + token[-4:]

    def _is_valid_jwt(self, token: str) -> bool:
        """Basic JWT format validation."""
        parts = token.split('.')
        return len(parts) == 3 and all(len(part) > 0 for part in parts)
```

## Performance Standards

### Memory Management
```python
class MemoryEfficientQueueManager:
    """Queue manager with memory optimization."""

    def __init__(self, max_prompts_in_memory: int = 1000):
        self.max_prompts_in_memory = max_prompts_in_memory
        self._prompts_cache: List[SunoPrompt] = []
        self._prompt_disk_storage = Path("data/prompts_cache.jsonl")

    def load_prompts(self, prompts: List[SunoPrompt]) -> None:
        """Load prompts with memory optimization."""
        if len(prompts) <= self.max_prompts_in_memory:
            self._prompts_cache = prompts
        else:
            # Store overflow on disk
            self._prompts_cache = prompts[:self.max_prompts_in_memory]
            self._save_prompts_to_disk(prompts[self.max_prompts_in_memory:])

    def get_prompt(self, index: int) -> SunoPrompt:
        """Get prompt with lazy loading from disk."""
        if index < len(self._prompts_cache):
            return self._prompts_cache[index]

        # Load from disk if not in memory
        return self._load_prompt_from_disk(index)

    def __del__(self):
        """Cleanup resources on deletion."""
        if hasattr(self, '_temp_files'):
            for temp_file in self._temp_files:
                try:
                    temp_file.unlink()
                except Exception:
                    pass
```

### Async Operations (Future Enhancement)
```python
# Note: Currently using synchronous operations, but prepared for async migration
class AsyncDownloadManager:
    """Async download manager for future performance improvements."""

    async def download_songs_async(
        self,
        songs: List[SongClip],
        max_concurrent: int = 3
    ) -> List[DownloadResult]:
        """Download songs concurrently with async operations."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_single(song: SongClip) -> DownloadResult:
            async with semaphore:
                return await self._download_song_impl(song)

        # Create tasks for concurrent download
        tasks = [download_single(song) for song in songs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if isinstance(r, DownloadResult)]
```

## Git Workflow và Version Control

### Commit Message Standards
```
Format: <type>(<scope>): <description>

Types:
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Code formatting (no functional change)
refactor: Code refactoring
test: Test additions/changes
chore: Build process or dependency changes

Examples:
feat(queue): Add multi-queue orchestration system
fix(auth): Resolve session token expiry handling
docs(readme): Update installation instructions
refactor(session): Extract Chrome profile management
```

### Branch Strategy
```
main                    # Production-ready code
├── develop            # Integration branch
├── feature/queue-system    # Feature branches
├── feature/download-ui
├── fix/session-expiry      # Bug fix branches
└── hotfix/critical-fix     # Emergency fixes
```

## Code Review Process

### Review Checklist
- **Functionality**: Code works as expected
- **Architecture**: Follows clean architecture principles
- **Type Safety**: Proper type hints and validation
- **Error Handling**: Comprehensive exception management
- **Testing**: Adequate test coverage
- **Documentation**: Clear docstrings and comments
- **Performance**: No obvious performance issues
- **Security**: No security vulnerabilities

### Review Process
1. **Self-Review**: Developer reviews own code first
2. **Peer Review**: Another developer reviews changes
3. **Automated Checks**: CI/CD pipeline validates code
4. **Integration Testing**: Test in development environment
5. **Deployment**: Merge to main after approval

---

**Document Status**: Complete
**Last Updated**: 18/11/2025
**Next Review**: 25/11/2025
**Version**: 2.0

This document establishes the coding standards, conventions, and best practices for the Suno Account Manager project. These standards ensure code quality, maintainability, and consistency across all contributions.

---

## 🐍 Python Code Standards

### 1. Language Version & Compatibility
- **Python Version**: 3.10+ (required)
- **Type Hints**: Required for all public methods and functions
- **Docstrings**: Required for all classes, methods, and functions
- **Encoding**: UTF-8 for all Python files

### 2. Code Style (PEP 8 Compliance)

#### 2.1 Basic Formatting
```python
# ✅ Correct - PEP 8 compliant
class AccountManager:
    """Manages Suno accounts and their metadata."""

    def __init__(self) -> None:
        """Initialize the account manager."""
        self.accounts: Dict[str, Account] = {}
        self.load_accounts()

    def add_account(self, name: str, email: str) -> bool:
        """Add new account to the system.

        Args:
            name: Account name (must be unique)
            email: Account email address

        Returns:
            True if account was added successfully, False otherwise
        """
        if name in self.accounts:
            logger.warning(f"Account {name} already exists")
            return False

        # Implementation here
        return True

# ❌ Incorrect - Not PEP 8 compliant
class accountmanager:
    def __init__(self):
        self.accounts={}
    def addAccount(self,name,email):
        if name in self.accounts:return False
```

#### 2.2 Import Organization
```python
# Standard library imports first
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Third-party imports next
import customtkinter as ctk
from selenium import webdriver
import requests

# Local imports last
from config.settings import ACCOUNTS_FILE, PROFILES_DIR
from src.models import Account
from src.utils import load_json, save_json, logger
```

#### 2.3 Line Length & Indentation
- **Maximum Line Length**: 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Continuation**: Hanging indent for multiline statements

```python
# ✅ Correct line handling
def long_function_name(
    param1: str,
    param2: int,
    param3: Optional[Dict[str, str]] = None
) -> bool:
    """Function with long parameter list properly formatted."""
    if param1 and param2 > 0:
        return True
    return False

# ✅ Correct continuation
result = some_very_long_function_name(
    parameter1,
    parameter2,
    parameter3
) if condition else default_value
```

### 3. Naming Conventions

#### 3.1 Variables and Functions
```python
# ✅ Correct - snake_case
user_account_name = "john_doe"
download_history_list = []
current_session_token = None

def get_session_token() -> Optional[str]:
    """Retrieve the current session token."""
    pass

def create_chrome_options(profile_path: Path) -> webdriver.ChromeOptions:
    """Create Chrome options with specified profile path."""
    pass
```

#### 3.2 Classes and Constants
```python
# ✅ Correct - PascalCase for classes
class AccountManager:
    pass

class DownloadHistory:
    pass

# ✅ Correct - UPPER_CASE for constants
MAX_CONCURRENT_DOWNLOADS = 3
DEFAULT_TIMEOUT = 300
SESSION_TOKEN_EXPIRY = 3600 * 24
```

#### 3.3 Private and Protected Members
```python
class SessionManager:
    """Manages browser sessions."""

    def __init__(self) -> None:
        # Private attributes (single underscore)
        self._driver: Optional[webdriver.Chrome] = None
        self._session_token: Optional[str] = None

        # Public attributes
        self.profile_path: Path = Path()

    def _create_chrome_options(self) -> webdriver.ChromeOptions:
        """Private method for creating Chrome options."""
        pass

    def get_session_token(self) -> Optional[str]:
        """Public method for retrieving session token."""
        return self._session_token
```

---

## 📁 File & Directory Organization

### 1. Directory Structure Standards
```
src/
├── ui/                             # UI Components (Presentation Layer)
│   ├── __init__.py
│   ├── main_window.py              # Main application window
│   ├── account_panel.py            # Account management panel
│   ├── components/                 # Reusable UI components
│   │   ├── __init__.py
│   │   └── advanced_options_widget.py
│   └── ...
│
├── core/                           # Business Logic (Application Layer)
│   ├── __init__.py
│   ├── account_manager.py          # Account management logic
│   ├── session_manager.py          # Session handling
│   └── ...
│
├── models/                         # Data Models (Domain Layer)
│   ├── __init__.py
│   └── data_models.py              # Core data structures
│
└── utils/                          # Utilities (Infrastructure Layer)
    ├── __init__.py
    ├── logger.py                   # Logging utilities
    └── helpers.py                  # Helper functions
```

### 2. File Naming Conventions
```python
# ✅ Correct - snake_case
account_manager.py
download_history.py
advanced_options_widget.py
suno_api_client.py

# ✅ Correct - Descriptive names
batch_song_creator.py      # Clear purpose
metadata_handler.py        # Clear functionality
form_automation.py         # Descriptive

# ❌ Incorrect - Avoid
mgr.py                     # Too abbreviated
utils.py                   # Too generic
stuff.py                   # Not descriptive
```

### 3. Module Organization
```python
# ✅ Correct module structure in __init__.py
"""
UI Package - User interface components for Suno Account Manager
"""

from .main_window import MainWindow, run_app
from .account_panel import AccountPanel
from .download_panel import DownloadPanel

__all__ = [
    'MainWindow',
    'run_app',
    'AccountPanel',
    'DownloadPanel'
]
```

---

## 🏗️ Architecture Patterns

### 1. Clean Architecture Implementation
```python
# ✅ Correct - Dependency flow: UI → Core → Models → Utils
class AccountPanel:
    """UI panel for account management."""

    def __init__(self, parent, account_manager: AccountManager):
        """Initialize with dependency injection."""
        super().__init__(parent)
        self.account_manager = account_manager  # Core layer dependency
        self.create_ui()

    def on_add_account_clicked(self) -> None:
        """Handle add account button click."""
        name = self.name_entry.get()
        email = self.email_entry.get()

        # Delegate to core layer
        success = self.account_manager.add_account(name, email)

        if success:
            self.show_success_message(f"Account {name} added successfully")
        else:
            self.show_error_message(f"Failed to add account {name}")

# ❌ Incorrect - Direct infrastructure access from UI
class AccountPanel:
    def save_account_to_file(self, account_data: dict) -> None:
        """Don't do this - UI shouldn't handle file operations."""
        with open('accounts.json', 'w') as f:
            json.dump(account_data, f)  # Infrastructure concern
```

### 2. Factory Pattern Implementation
```python
# ✅ Correct - Factory for creating drivers
class StealthDriverFactory:
    """Factory for creating stealth Chrome drivers."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.37",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.38"
    ]

    @classmethod
    def create_driver(cls, profile_path: Path, headless: bool = False) -> webdriver.Chrome:
        """Create a stealth Chrome driver with random user agent."""
        options = Options()
        options.add_argument(f'--user-data-dir={profile_path}')

        # Random user agent for anti-detection
        user_agent = random.choice(cls.USER_AGENTS)
        options.add_argument(f'--user-agent={user_agent}')

        return webdriver.Chrome(options=options)
```

### 3. Observer Pattern for UI Updates
```python
# ✅ Correct - Callback-based progress updates
class DownloadManager:
    """Manages download operations with progress callbacks."""

    def batch_download(
        self,
        clips: List[SongClip],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, int]:
        """Download multiple clips with progress reporting."""
        total = len(clips)

        for idx, clip in enumerate(clips, 1):
            if progress_callback:
                progress_callback(f"Downloading {clip.title}...", (idx-1) * 100 // total)

            # Download logic here

            if progress_callback:
                progress_callback(f"Completed {clip.title}", idx * 100 // total)

        return {'success': total, 'failed': 0}
```

---

## 📝 Documentation Standards

### 1. Docstring Format (Google Style)
```python
def extract_session_token(
    driver: webdriver.Chrome,
    timeout: int = 10,
    retry_count: int = 3
) -> Optional[str]:
    """Extract session token from browser cookies.

    This function searches for the __session cookie in the current browser
    instance and returns its value for authentication purposes.

    Args:
        driver: Chrome WebDriver instance with active session
        timeout: Maximum time to wait for cookie extraction in seconds
        retry_count: Number of retry attempts if extraction fails

    Returns:
        Session token string if found, None otherwise

    Raises:
        WebDriverException: If browser becomes unresponsive
        TimeoutError: If token extraction exceeds timeout period

    Example:
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://suno.com")
        >>> token = extract_session_token(driver)
        >>> print(f"Token: {token[:10]}...")
    """
    # Implementation here
    pass
```

### 2. Class Documentation
```python
class AccountManager:
    """Manages Suno accounts and their metadata.

    This class provides CRUD operations for Suno.com accounts, including
    adding new accounts, updating existing ones, and managing Chrome profiles
    for session persistence.

    Attributes:
        accounts: Dictionary mapping account names to Account objects
        profiles_dir: Directory path for Chrome profiles storage

    Note:
        All account data is persisted to JSON files for recovery across
        application restarts. Chrome profiles contain complete browser
        state including cookies and localStorage.
    """

    def __init__(self, profiles_dir: Optional[Path] = None) -> None:
        """Initialize AccountManager with optional custom profiles directory."""
        # Implementation
        pass
```

### 3. Inline Comments
```python
def validate_xml_structure(self, xml_content: str) -> bool:
    """Validate XML content structure for song creation."""
    try:
        # Parse XML content
        root = ET.fromstring(xml_content)

        # Check for required tags
        required_tags = ['TITLE', 'LYRICS', 'STYLE']
        for tag in required_tags:
            element = root.find(tag)
            if element is None or not element.text:
                logger.warning(f"Missing or empty tag: {tag}")
                return False

            # Validate content length
            if tag == 'TITLE' and len(element.text.strip()) < 1:
                logger.error("Title cannot be empty")
                return False

        return True

    except ET.ParseError as e:
        logger.error(f"XML parsing failed: {e}")
        return False
```

---

## 🧪 Testing Standards

### 1. Test File Organization
```python
# tests/test_account_manager.py
"""Tests for AccountManager class."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.account_manager import AccountManager
from src.models import Account

class TestAccountManager:
    """Test suite for AccountManager."""

    def setup_method(self) -> None:
        """Setup test environment before each test."""
        self.temp_dir = Path("/tmp/test_suno")
        self.temp_dir.mkdir(exist_ok=True)

        # Patch settings for testing
        with patch('src.core.account_manager.ACCOUNTS_FILE', self.temp_dir / "test_accounts.json"):
            self.account_manager = AccountManager()

    def test_add_account_success(self) -> None:
        """Test successful account addition."""
        # Arrange
        name = "test_account"
        email = "test@example.com"

        # Act
        result = self.account_manager.add_account(name, email)

        # Assert
        assert result is True
        account = self.account_manager.get_account(name)
        assert account is not None
        assert account.email == email
        assert account.name == name
```

### 2. Test Naming Conventions
```python
# ✅ Correct - Descriptive test names
def test_add_duplicate_account_returns_false():
    """Test adding duplicate account returns False."""
    pass

def test_session_token_extraction_with_valid_cookie():
    """Test token extraction works with valid session cookie."""
    pass

def test_download_progress_callback_reports_correct_percentages():
    """Test progress callback reports accurate percentages."""
    pass

# ❌ Incorrect - Vague test names
def test_add():
    """Test add function."""  # What are we adding?
    pass

def test_works():
    """Test that it works."""  # What works?
    pass
```

### 3. Mock and Patch Standards
```python
# ✅ Correct - Proper mocking of external dependencies
@patch('src.core.session_manager.webdriver.Chrome')
@patch('src.core.session_manager.PROFILES_DIR')
def test_launch_browser_with_valid_profile(self, mock_profiles_dir, mock_chrome):
    """Test browser launch with valid profile."""
    # Arrange
    mock_profiles_dir.__truediv__ = Mock(return_value=Path("/valid/profile"))
    mock_driver = Mock()
    mock_chrome.return_value = mock_driver

    # Act
    result = SessionManager.launch_browser("test_account")

    # Assert
    assert result is not None
    mock_chrome.assert_called_once()
    mock_driver.get.assert_called_once_with("https://suno.com")
```

---

## 🔧 Configuration & Settings

### 1. Settings File Structure
```python
# config/settings.py
"""
Application settings and configuration constants.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
PROFILES_DIR = BASE_DIR / "profiles"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# Application settings
APP_NAME = "Suno Account Manager"
APP_VERSION = "2.0.0"
APP_WIDTH = 1400
APP_HEIGHT = 850

# UI Theme Configuration
THEME = "dark-blue"
APPEARANCE_MODE = "dark"  # Options: "dark", "light", "system"

# Colors (consistent theme colors)
COLORS = {
    "primary": "#1f538d",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "dark": "#2c3e50",
    "light": "#ecf0f1"
}

# API Configuration
SUNO_URL = "https://suno.com"
SUNO_API_URL = "https://studio-api.prod.suno.com/api"
API_TIMEOUT = 30
MAX_RETRIES = 3

# Browser Configuration
CHROME_OPTIONS = [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage'
]

# Download Settings
DEFAULT_DOWNLOAD_LIMIT = 10
MAX_CONCURRENT_DOWNLOADS = 3
DOWNLOAD_TIMEOUT = 300
DELAY_BETWEEN_DOWNLOADS = 2
```

### 2. Environment-Specific Configuration
```python
# config/settings.py (continued)
import os

# Environment-specific settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'False').lower() == 'true'

# Override settings for development
if DEBUG:
    LOG_LEVEL = 'DEBUG'
    HEADLESS_BROWSER = False
    DOWNLOAD_TIMEOUT = 60  # Longer timeout for debugging
```

---

## 🔍 Error Handling & Logging

### 1. Logging Standards
```python
# src/utils/logger.py
"""Centralized logging configuration."""

import logging
from pathlib import Path
from datetime import datetime

class SunoLogger:
    """Custom logger for Suno Account Manager."""

    def __init__(self, name: str = "suno_app"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure logger with file and console handlers."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Generate log filename with current date
        log_file = logs_dir / f"suno_app_{datetime.now().strftime('%Y%m%d')}.log"

        # File handler for detailed logging
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

# Global logger instance
logger = SunoLogger().logger
```

### 2. Error Handling Patterns
```python
# ✅ Correct - Comprehensive error handling
def download_clip(self, clip: SongClip, output_dir: Path) -> bool:
    """Download a single clip with comprehensive error handling."""
    try:
        logger.info(f"Starting download: {clip.title}")

        # Validate inputs
        if not clip.audio_url:
            logger.error(f"No audio URL for clip: {clip.title}")
            return False

        if not output_dir.exists():
            logger.error(f"Output directory does not exist: {output_dir}")
            return False

        # Attempt download
        audio_path = self._download_audio_file(clip.audio_url, output_dir)

        if not audio_path:
            logger.error(f"Failed to download audio for: {clip.title}")
            return False

        logger.info(f"Successfully downloaded: {clip.title}")
        return True

    except requests.RequestException as e:
        logger.error(f"Network error downloading {clip.title}: {e}")
        return False

    except IOError as e:
        logger.error(f"File system error for {clip.title}: {e}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error downloading {clip.title}: {e}")
        return False

# ❌ Incorrect - Poor error handling
def download_clip(self, clip, output_dir):
    try:
        # Download logic
        return True
    except:
        # Too broad exception handling
        return False
```

---

## 📊 Performance Standards

### 1. Memory Management
```python
# ✅ Correct - Proper resource management
def process_large_file_list(self, file_paths: List[Path]) -> None:
    """Process many files efficiently using generators."""

    def process_batch(batch: List[Path]) -> None:
        """Process a batch of files."""
        for file_path in batch:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Process content
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
            finally:
                # File automatically closed by context manager
                pass

    # Process files in batches to manage memory
    BATCH_SIZE = 100
    for i in range(0, len(file_paths), BATCH_SIZE):
        batch = file_paths[i:i + BATCH_SIZE]
        process_batch(batch)

        # Force garbage collection for large batches
        if i % (BATCH_SIZE * 10) == 0:
            import gc
            gc.collect()
```

### 2. Async Operations
```python
# ✅ Correct - Asynchronous UI updates
def start_download_async(self, clips: List[SongClip]) -> None:
    """Start download process without blocking UI."""

    def download_worker() -> None:
        """Worker function running in background thread."""
        try:
            results = self.download_manager.batch_download(
                clips,
                progress_callback=self.update_progress_callback
            )

            # Update UI on main thread
            self.after(0, self.on_download_complete, results)

        except Exception as e:
            logger.error(f"Download worker error: {e}")
            self.after(0, self.on_download_error, str(e))

    # Start worker thread
    import threading
    thread = threading.Thread(target=download_worker, daemon=True)
    thread.start()

    # Update UI immediately
    self.status_label.configure(text="Download started...")
```

---

## ✅ Code Review Checklist

### Before Submitting Code

#### [ ] Code Style
- [ ] Follows PEP 8 conventions
- [ ] Line length ≤ 100 characters
- [ ] Proper import organization
- [ ] Consistent naming conventions

#### [ ] Documentation
- [ ] All public methods have docstrings
- [ ] Docstrings follow Google style
- [ ] Complex logic has inline comments
- [ ] README/requirements updated if needed

#### [ ] Error Handling
- [ ] Proper exception handling
- [ ] Comprehensive logging
- [ ] Graceful degradation
- [ ] User-friendly error messages

#### [ ] Testing
- [ ] New features have unit tests
- [ ] Tests pass consistently
- [ ] Test coverage is adequate
- [ ] Integration tests updated

#### [ ] Architecture
- [ ] Follows clean architecture
- [ ] Proper dependency injection
- [ ] No circular imports
- [ ] Single responsibility principle

#### [ ] Performance
- [ ] No memory leaks
- [ ] Efficient algorithms
- [ ] Proper resource cleanup
- [ ] UI remains responsive

---

## 🔧 Development Tools & Setup

### 1. Required Development Tools
```bash
# Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Additional dev tools

# Code formatting
pip install black isort flake8

# Type checking
pip install mypy

# Testing
pip install pytest pytest-cov pytest-mock
```

### 2. Pre-commit Hooks Setup
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### 3. IDE Configuration (VS Code)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.rulers": [100],
    "editor.tabSize": 4,
    "editor.insertSpaces": true
}
```

---

## 📚 Resources & References

### Style Guides
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code principles by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350884)

### Documentation Standards
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)

### Testing Best Practices
- [pytest documentation](https://docs.pytest.org/en/stable/)
- [Python Testing with pytest](https://realpython.com/pytest-python-testing/)

---

*This code standards document is a living document and will be updated as the project evolves. All contributors are expected to follow these standards and suggest improvements when appropriate.*