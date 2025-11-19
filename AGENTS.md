<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md - Hướng Dẫn Chỉnh Sửa Nội Dung

**Audience:** All developers, AI coding agents
**Applies to:** Entire repository
**Scope:** General guidelines, project conventions, cross-cutting concerns
**Last reviewed:** 2025-11-18
**Owners:** Core team

---

## 📝 Hướng Dẫn Cập Nhật Nội Dung

### 🎯 Mục Đích Tài Liệu
Tài liệu này cung cấp hướng dẫn chi tiết cho AI agents và developers khi làm việc với codebase Suno Account Manager v2.0.

### 📋 Quy Tắc Golden (MUST REMEMBER)
1. **Language**: Think in **ENGLISH** but respond in **VIETNAMESE**
2. **Context7 MCP**: Luôn dùng Context7 MCP để lấy latest library information
3. **No Hard-coded**: Tránh hard-coding values trừ khi absolutely necessary
4. **Type Safety**: Không dùng `any` hoặc `unknown` types trong TypeScript/Python
5. **No Classes**: Không dùng Python `class` trừ khi absolutely necessary

---

## 📂 Module-Specific Guidelines

For detailed guidance on specific parts of the codebase, see module-specific `AGENTS.md` files:

| Module | File | Key Topics |
|--------|------|-----------|
| **Core Layer** | [`src/core/AGENTS.md`](src/core/AGENTS.md) | Manager lifecycle, session patterns, queue workflows, API integration, browser automation |
| **UI Layer** | [`src/ui/AGENTS.md`](src/ui/AGENTS.md) | Panel patterns, component structure, threading model, CustomTkinter conventions |
| **Configuration** | [`config/AGENTS.md`](config/AGENTS.md) | Path constants, JSON persistence, settings precedence, style config |
| **Legacy CLI** | [`legacy_modules/AGENTS.md`](legacy_modules/AGENTS.md) | CLI interface, standalone usage, migration guide |
| **Testing** | [`tests/AGENTS.md`](tests/AGENTS.md) | Test structure, mocking patterns, fixture conventions, integration testing |

**Start here for general guidelines. Dive into module files for specific patterns.**

---

## 🏗️ Kiến Trúc Dự Án (Clean Architecture)

### 4 Layers Architecture
```
┌─────────────────────────────────────────────────┐
│         Presentation Layer (src/ui/)            │
│   MainWindow, AccountPanel, DownloadPanel,     │
│   HistoryPanel, MultipleSongsPanel             │
└────────────────────┬────────────────────────────┘
                     │ depends on
┌────────────────────▼────────────────────────────┐
│       Application Layer (src/core/)             │
│  AccountManager, SessionManager, DownloadMgr,  │
│  BatchSongCreator, QueueManager                 │
└────────────────────┬────────────────────────────┘
                     │ depends on
┌────────────────────▼────────────────────────────┐
│         Domain Layer (src/models/)              │
│   Account, SongClip, DownloadHistory, Queue     │
└────────────────────┬────────────────────────────┘
                     │ uses
┌────────────────────▼────────────────────────────┐
│      Infrastructure Layer (src/utils/)          │
│   Logger, Helpers, StealthDriver                │
└─────────────────────────────────────────────────┘
```

**Dependency Rules**: UI → Core → Models → Utils (không import ngược)

---

## 📁 Cấu Trúc Project Đáng Chú Ý

### Quy Tắc Import
```python
# ✅ ĐÚNG - Chỉ đi xuống layers
from src.core.account_manager import AccountManager
from src.models.data_models import Account
from src.utils.logger import logger

# ❌ SAI - Import ngược lên layers
from src.ui.main_window import MainWindow  # Không được trong core/
```

### Key Directories
```
F:\auto-suno-app\
├── app.py                          # Entry point - CustomTkinter GUI
├── config/
│   ├── settings.py                 # Centralized configuration
│   └── style_config.py             # UI styling configuration
├── src/
│   ├── ui/                         # Presentation Layer
│   │   ├── main_window.py          # Main GUI với 6 tabs
│   │   ├── account_panel.py        # Account management UI
│   │   ├── multiple_songs_panel.py # Queue system UI
│   │   ├── create_music_panel.py   # Simple creation UI
│   │   ├── download_panel.py       # Download configuration
│   │   ├── history_panel.py        # Download history
│   │   └── song_creation_history_panel.py  # Creation history + CSV
│   ├── core/                       # Application Layer
│   │   ├── account_manager.py      # Account CRUD + persistence
│   │   ├── session_manager.py      # Chrome automation + tokens
│   │   ├── queue_manager.py        # Queue CRUD + state persistence
│   │   ├── batch_song_creator.py   # Multi-queue execution engine
│   │   ├── song_creation_history_manager.py  # History tracking
│   │   └── download_manager.py     # Download orchestration
│   ├── models/
│   │   └── data_models.py          # Domain models (Account, Queue, etc.)
│   └── utils/
│       ├── logger.py               # Singleton logger
│       ├── helpers.py              # JSON I/O utilities
│       ├── stealth_driver.py       # Anti-detection ChromeDriver
│       └── prompt_parser.py        # XML parsing
├── data/                           # Runtime data (gitignored)
│   ├── suno_accounts.json          # Account database
│   ├── queue_state.json            # Queue state persistence
│   ├── song_creation_history.json  # Creation history
│   └── download_history.json       # Download tracking
├── profiles/                       # Chrome profiles (gitignored)
├── downloads/                      # Downloaded songs (gitignored)
└── logs/                           # Application logs (gitignored)
```

---

## 🚀 Build, Test, and Development Commands

### Environment Setup
```powershell
# Create isolated environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run the application
python app.py

# Legacy CLI testing
python legacy_modules/suno_batch_download.py --help
```

### Quality Assurance
```bash
# Lint/sanity check
python -m compileall src

# Run tests
pytest
python -m pytest tests

# Monitor logs while debugging
Get-Content logs/app_*.log -Wait
```

---

## 🎨 Coding Style & Naming Conventions

### Python Standards
- **Target**: Python >=3.10
- **Style**: PEP 8 compliance (4 spaces indentation)
- **Type Hints**: Exhaustive type hints cho public methods
- **Docstrings**: Module-level docstrings required

### Naming Patterns
```python
# Classes (UI components): PascalCase
class MainWindow:
class AccountPanel:

# Functions/Variables: snake_case
def create_account():
account_name = "test_account"

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_BATCH_SIZE = 5

# File names: lowercase_with_underscores
account_manager.py
data_models.py
```

### Logging Convention
```python
from src.utils.logger import logger

# ✅ Use logger instead of print()
logger.info("User action completed")
logger.error(f"Operation failed: {error}")
logger.debug(f"Debug info: {data}")

# ❌ Avoid print()
print("Debug message")  # Don't do this
```

### Path Management
```python
# ✅ Import from config - don't duplicate
from config.settings import PROFILES_DIR, DOWNLOADS_DIR

# ❌ Don't hardcode paths
PROFILES_DIR = "F:/auto-suno-app/profiles"  # Don't do this
```

---

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── test_queue_manager.py
├── test_batch_song_creator.py
├── test_session_manager.py
├── integration/
│   ├── test_queue_workflow.py
│   └── test_queue_stress.py
└── fixtures/
    └── sample_prompts.xml
```

### Testing Best Practices
```python
# Use pytest with descriptive names
def test_queue_manager_add_queue_success():
    """Test adding queue to manager succeeds."""

# Mock external dependencies
from unittest.mock import Mock, patch

@patch('src.core.session_manager.StealthDriver')
def test_session_creation_with_mock_driver(mock_driver):
    # Test logic without actual browser
    pass
```

### Coverage Priorities
1. **Account persistence** - CRUD operations
2. **Session token retrieval** - Authentication flow
3. **Queue workflows** - State persistence
4. **Download orchestration** - Error handling

---

## 🔄 Workflow When Implementing Features

### 1. Planning Phase
```python
# Read relevant documentation first
with open('README.md', 'r') as f:
    project_context = f.read()

# Check existing patterns
grep -r "queue_manager" src/ --include="*.py"
```

### 2. Implementation Phase
```python
# Follow dependency injection pattern
class MultipleSongsPanel:
    def __init__(self, parent, queue_manager: QueueManager):
        self.queue_manager = queue_manager
```

### 3. Testing Phase
```python
# Add regression test for new feature
def test_new_feature_regression():
    """Ensure new feature doesn't break existing functionality."""
    pass
```

---

## 📋 Commit & Pull Request Guidelines

### Commit Convention
```
feat(scope): description
fix(scope): description
docs(scope): description
refactor(scope): description
test(scope): description

Examples:
feat(core): add queue state persistence
fix(ui): resolve IntVar crash in batch size
docs(readme): update installation guide
```

### PR Requirements
1. **Motivation**: Why this change is needed
2. **Testing Evidence**: `pytest` results, `python app.py` smoke test
3. **Documentation**: Updated relevant docs if needed
4. **Screenshots/Logs**: For UI-visible changes
5. **Linked Issues**: Reference any related task IDs

### Version Management
- Update `CHANGELOG.md` for functional changes
- Bump version in `versions.json`
- Reference module touched in commit

---

## 🚨 Critical Rules (NO EXCEPTIONS)

### Security Rules
1. **Chrome profiles**: NEVER commit to git
2. **Sensitive data**: All JSON files in `data/` gitignored
3. **Session tokens**: Refresh every 24h maximum
4. **Personal accounts**: Only use your own accounts

### Architecture Rules
1. **Import direction**: Only downward (UI → Core → Models → Utils)
2. **Path constants**: Always import from `config.settings`
3. **Singleton patterns**: Logger is singleton - don't instantiate multiple
4. **Error handling**: Use logger, not print(), for errors

### Code Quality Rules
1. **No classes**: Avoid Python classes unless absolutely necessary
2. **Type safety**: No `any` or `unknown` types
3. **Hard-coded values**: Avoid unless absolutely necessary
4. **Documentation**: Update docs when behavior changes

---

## 📚 Documentation Management

### Required Documentation Updates
When implementing features, update:
1. **CLAUDE.md** - If adding new patterns or workflows
2. **README.md** - If user-facing features change
3. **docs/** folder - Technical documentation
4. **CHANGELOG.md** - For all functional changes

### Memory Bank Integration
- Project briefs: `memory-bank/briefs/`
- System context: `memory-bank/context/`
- Task histories: `memory-bank/tasks/`
- Update these when behavior or scope shifts

---

## 🛠️ Advanced Patterns

### State Persistence
```python
# Queue state persistence example
def save_queue_state(self, queues: List[QueueEntry]):
    state_data = {
        "queues": [queue.to_dict() for queue in queues],
        "timestamp": datetime.now().isoformat()
    }
    write_json("data/queue_state.json", state_data)
```

### Error Recovery
```python
# Continue on individual failures
def process_batch(self, songs: List[SongData]):
    for song in songs:
        try:
            self.create_song(song)
        except Exception as e:
            logger.error(f"Song creation failed: {e}")
            continue  # Continue with next song
```

### Progress Callbacks
```python
# UI progress updates
def on_progress_callback(self, current: int, total: int, message: str):
    progress_percent = (current / total) * 100
    self.progress_bar.set(progress_percent / 100)
    self.status_label.configure(text=message)
```

---

## 📊 Current Feature Set (v2.1.0)

### Core Features
1. **Multi-Queue Management** - Multiple accounts, parallel execution
2. **Session Persistence** - 24h Chrome profile sessions
3. **Batch Download** - MP3 + ID3 metadata
4. **Anti-CAPTCHA** - Stealth driver, human delays
5. **History Tracking** - Creation + download history with CSV export

### UI Components
- **6 Tabs**: Accounts, Queue (Multi), Create (Simple), Download, Download History, Creation History
- **Queue Management**: Add, start, pause, resume, delete queues
- **Progress Tracking**: Real-time progress bars and status updates
- **Export Functionality**: CSV export for creation history

### Integration Points
- **Suno.com API** - Reverse engineered endpoints
- **Chrome WebDriver** - Browser automation with stealth
- **Clerk Authentication** - JWT token management
- **File System** - Profile isolation, download organization

---

This documentation serves as the authoritative guide for all AI agents and developers working on the Suno Account Manager project. When in doubt, refer to this document first, then check module-specific AGENTS.md files for detailed patterns.
