# Suno Account Manager - Backend Integration Analysis

## Core Manager Interfaces

### AccountManager
**CRUD Operations:**
- `add_account(name, email)` → bool
- `get_account(name)` → Account | None
- `update_account(name, **kwargs)` → bool
- `rename_account(old, new)` → bool
- `delete_account(name, delete_profile=False)` → bool
- `get_all_accounts()` → List[Account]
- `update_last_used(name)` → None
- `get_profile_path(name)` → Path | None

### QueueManager
**Orchestration Methods:**
- `add_queue_entry(account, total_songs, songs_per_batch, prompts)` → QueueEntry
- `get_pending_queues()` → List[QueueEntry]
- `update_queue_progress(queue_id, completed_count, status)` → bool
- `get_all_queues()` → List[QueueEntry]
- `remove_queue_entry(queue_id)` → bool
- `clear()` → None

### DownloadManager
**Core Methods:**
- `fetch_clips(session_token, profile_name=None, use_create_page=False)` → List[SongClip]
- `download_clip(session_token, clip, output_dir, with_thumbnail=True, append_uuid=True, progress_callback=None)` → bool
- `batch_download_paginated(account_name, session_token, output_dir, profile_name=None, use_create_page=False, ...)` → Dict[str, int]

### SessionManager
**Chrome Automation:**
- `launch_browser(account_name, headless=False)` → webdriver.Chrome | None
- `get_session_token(account_name)` → str | None
- `get_session_token_from_me_page(account_name)` → (str, webdriver.Chrome) | (None, None)
- `verify_session(account_name)` → bool

### BatchSongCreator
**Multi-tab Execution:**
- `create_songs_batch(prompts, songs_per_session, advanced_options, auto_submit, progress_callback, account_name=None, history_manager=None)` → List[Dict]

## Data Models Structure

```python
@dataclass
class Account:
    name: str
    email: str
    created_at: str
    last_used: Optional[str]
    status: str

@dataclass
class QueueEntry:
    id: str
    account_name: str
    total_songs: int
    songs_per_batch: int
    prompts_range: Tuple[int, int]
    status: str
    created_at: str
    completed_count: int

@dataclass
class SongClip:
    id: str
    title: str
    audio_url: Optional[str]
    image_url: Optional[str]
    tags: str
    created_at: Optional[str]
    duration: Optional[float]

@dataclass
class SunoPrompt:
    title: str
    lyrics: str
    style: str
```

## IPC Integration Strategy

### Critical IPC Exposure Points:

**Account Management:**
- `create_account(name, email)` → Account
- `get_accounts()` → List[Account]
- `delete_account(name, delete_profile=False)` → bool
- `get_session_token(name)` → str | None

**Queue Management:**
- `add_to_queue(account, prompts, songs_per_batch)` → QueueEntry
- `get_queue_status()` → List[QueueEntry]
- `update_queue_progress(queue_id, progress, status)` → bool
- `cancel_queue(queue_id)` → bool

**Download Management:**
- `start_download(account, profile_name, use_create_page, ...)` → DownloadTask
- `get_download_progress(task_id)` → DownloadTask
- `cancel_download(task_id)` → bool
- `get_download_history(account)` → List[SongClip]

**Song Creation:**
- `create_batch_songs(account, prompts, advanced_options, auto_submit)` → List[Dict]
- `stop_creation()` → None
- `get_creation_progress()` → List[SongCreationRecord]

### Progress Translation:
- Python callbacks → Electron IPC events
- Real-time progress updates → React state updates
- Error propagation → Error events
- Completion notifications → Success events

## Error Handling Patterns
- QueueValidationError for queue operations
- Chrome automation exceptions
- API rate limiting and network errors
- File I/O and persistence errors

**Critical Integration Points:** Account session management, queue orchestration, download progress tracking, and batch creation workflow require robust IPC bridges.