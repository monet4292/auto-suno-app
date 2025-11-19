# AGENTS.md

**Audience:** AI coding agents, developers maintaining CLI tools  
**Applies to:** `legacy_modules/**/*.py`  
**Scope:** CLI interface, migration path, standalone usage  
**Last reviewed:** 2025-11-10  
**Owners:** Core team

---

## CLI Interface

### Purpose

Legacy modules provide **standalone CLI tools** for batch operations without GUI:

1. `suno_batch_download.py` - Download songs from Suno profiles
2. `suno_auto_create.py` - Automated song creation from XML prompts

**Status**: ✅ Maintained for backward compatibility. Must remain functional.

**Migration Path**: GUI (`src/`) is the primary interface. Legacy CLI for advanced users and automation scripts.

---

## Standalone Usage

### Batch Download CLI

```bash
# Help
python legacy_modules/suno_batch_download.py --help

# Download from profile
python legacy_modules/suno_batch_download.py \
    --profile @username \
    --limit 50 \
    --output downloads/username

# Download from "my songs"
python legacy_modules/suno_batch_download.py \
    --me \
    --account account_name \
    --limit 100 \
    --output downloads/my_songs
```

**Key features**:
- Uses same Chrome profile system as GUI
- Same session token extraction logic
- Supports both `/profile` and `/me` endpoints
- Progress bar in terminal (using `tqdm`)

### Auto Create CLI

```bash
# Help
python legacy_modules/suno_auto_create.py --help

# Create from XML prompts
python legacy_modules/suno_auto_create.py \
    --account account_name \
    --prompts prompts/batch-1.xml \
    --batch-size 5 \
    --headless
```

**Key features**:
- Reads XML prompts (same format as GUI)
- Batch creation with configurable batch size
- Optional headless mode
- Logs to console

---

## Architecture Differences

### CLI vs GUI

| Aspect | Legacy CLI | GUI (src/) |
|--------|-----------|-----------|
| **Entry point** | Direct script execution | `app.py` → `MainWindow` |
| **User interaction** | Command-line arguments | Interactive panels |
| **Progress feedback** | `tqdm` progress bar | CustomTkinter progress widgets |
| **Threading** | Synchronous (blocking) | Asynchronous (daemon threads) |
| **Session management** | Launch → extract → close | Launch → keep open → reuse |
| **Error handling** | Print to stderr, exit codes | MessageBox dialogs |

### Code Reuse

Legacy modules **duplicate some logic** from `src/core/`:

```python
# legacy_modules/suno_batch_download.py
# Has own session token extraction (similar to SessionManager)

def get_session_token(profile_name: str) -> str:
    # Similar to SessionManager.get_session_token_from_me_page()
    # but simplified for CLI
```

**Why duplication?**
- Legacy pre-dates Clean Architecture refactor
- CLI has different constraints (no UI imports)
- Maintains independence (CLI works without `src/`)

**Future**: Consider extracting common logic to `src/utils/` that both can import.

---

## Legacy Module Patterns

### Argument Parsing

Use `argparse` for CLI:

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch download songs from Suno",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--profile',
        help='Suno profile username (e.g., @username)',
        type=str
    )
    
    parser.add_argument(
        '--me',
        action='store_true',
        help='Download from "my songs" (requires --account)'
    )
    
    parser.add_argument(
        '--account',
        help='Account name for --me mode',
        type=str
    )
    
    parser.add_argument(
        '--limit',
        help='Maximum number of songs to download (0 = all)',
        type=int,
        default=10
    )
    
    parser.add_argument(
        '--output',
        help='Output directory',
        type=str,
        default='downloads'
    )
    
    return parser.parse_args()
```

### Progress Display

Use `tqdm` for terminal progress:

```python
from tqdm import tqdm

def download_clips(clips: List[dict]):
    with tqdm(total=len(clips), desc="Downloading") as pbar:
        for clip in clips:
            # Download work...
            pbar.update(1)
            pbar.set_description(f"Downloading {clip['title']}")
```

### Logging to Console

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Starting download...")
logger.error("Download failed: %s", error)
```

---

## Migration Guide

### From CLI to GUI

**User migration**:
1. Launch `python app.py`
2. Add account (uses same Chrome profile from CLI)
3. Use Download panel (same functionality as CLI)

**Advantages of GUI**:
- Visual progress tracking
- Multiple accounts management
- Queue system for batch operations
- Session reuse (no repeated logins)
- Error dialogs with recovery options

### When to Use CLI

**Use CLI when**:
- Automating with scripts (cron jobs, scheduled tasks)
- Running on headless servers (with `--headless`)
- Integrating with other tools (pipe output)
- Debugging without GUI overhead

**Use GUI when**:
- Interactive usage
- Managing multiple accounts
- Complex workflows (queue system)
- Need visual feedback

---

## Maintenance Guidelines

### Frozen API

**Rule**: Legacy CLI API is **frozen**. Do not break existing scripts.

```python
# ✅ ALLOWED: Add new optional arguments
parser.add_argument('--new-option', help='New feature', action='store_true')

# ❌ FORBIDDEN: Remove or rename required arguments
parser.add_argument('--profile-name', ...)  # Would break --profile users

# ❌ FORBIDDEN: Change default behavior
# If --limit defaulted to 10, must stay 10
```

### Bug Fixes Only

**Acceptable changes**:
- Fix crashes or data corruption
- Update selectors if Suno.com changes
- Improve error messages
- Performance optimizations

**Not acceptable**:
- New features (add to GUI instead)
- Refactoring for style (keep as-is)
- Breaking API changes

### Deprecation Process

If must deprecate:

1. **Mark deprecated** (add warning):
```python
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated. Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Keep working for now
```

2. **Document in README**:
```markdown
## Deprecated Features
- `--old-flag`: Use `--new-flag` instead (removed in v3.0)
```

3. **Wait 2+ versions** before removal

---

## Testing Legacy Modules

### Manual Testing

```bash
# Smoke test download
python legacy_modules/suno_batch_download.py \
    --profile @test_user \
    --limit 1 \
    --output /tmp/test_download

# Verify output
ls -la /tmp/test_download/*.mp3

# Smoke test create
python legacy_modules/suno_auto_create.py \
    --account test_account \
    --prompts tests/fixtures/test_prompts.xml \
    --batch-size 1
```

### Automated Testing

```python
# tests/test_legacy_cli.py
import subprocess
import pytest

def test_batch_download_help():
    """Test --help works"""
    result = subprocess.run(
        ["python", "legacy_modules/suno_batch_download.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout

def test_batch_download_invalid_args():
    """Test validation"""
    result = subprocess.run(
        ["python", "legacy_modules/suno_batch_download.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "error:" in result.stderr
```

---

## Common Issues

### Chrome Profile Lock

**Problem**: CLI fails with "Chrome instance exited" if GUI has profile open.

**Solution**: Close GUI before running CLI, or use different account.

```bash
# Error
$ python legacy_modules/suno_batch_download.py --me --account my_account
Error: Chrome instance exited

# Fix: Close GUI, then retry
$ python legacy_modules/suno_batch_download.py --me --account my_account
✅ Success
```

### Session Token Expired

**Problem**: CLI downloads fail with 401 Unauthorized.

**Solution**: Use GUI to re-login, then retry CLI.

```bash
# Error
$ python legacy_modules/suno_batch_download.py --me --account my_account
Error: 401 Unauthorized

# Fix steps:
1. python app.py
2. Go to Account panel
3. Click "🔄 Sử dụng tài khoản" (re-login)
4. Close GUI
5. Retry CLI
```

---

## Entry Points

| File | Purpose | Key Functions |
|------|---------|--------------|
| `suno_batch_download.py` | Download CLI | `parse_args()`, `get_session_token()`, `download_clips()`, `main()` |
| `suno_auto_create.py` | Create CLI | `parse_args()`, `load_prompts()`, `create_songs()`, `main()` |
| `README.md` | Documentation | Usage examples, CLI flags |

---

## Cross-References

- **Core logic**: See `src/core/AGENTS.md#session-patterns` for session token extraction
- **Profile structure**: See `config/AGENTS.md#path-constants` for profile paths
- **XML format**: See `src/core/AGENTS.md#prompt-templates` for prompt structure
- **Testing**: See `tests/AGENTS.md#cli-testing` for test patterns

---

**Questions?** Check root `AGENTS.md` for general project guidelines.
