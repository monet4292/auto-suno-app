# Core Components API Documentation

## Overview

This document provides comprehensive API documentation for the core components of the Suno Account Manager application.

## Table of Contents

- [QueueManager](#queuemanager)
- [SongCreationManager](#songcreationmanager)
- [AccountManager](#accountmanager)
- [DownloadManager](#downloadmanager)
- [BatchSongCreator](#batchsongcreator)

---

## QueueManager

### Overview
Manages queue entries and persistence for multi-account song creation operations.

### Class: `QueueManager`

#### Constructor
```python
def __init__(self, state_file: Path = QUEUE_STATE_FILE)
```
- **Parameters:**
  - `state_file` (Path): Path to the queue state persistence file
- **Description:** Initializes queue manager with default state or loads existing state from disk

#### Core Methods

##### `add_queue_entry()`
```python
def add_queue_entry(
    self,
    account_name: str,
    total_songs: int,
    songs_per_batch: int,
    prompts: List[SunoPrompt],
) -> QueueEntry
```
- **Parameters:**
  - `account_name` (str): Name of the account responsible for the queue
  - `total_songs` (int): Number of songs to create for this entry
  - `songs_per_batch` (int): Number of songs to create per browser session
  - `prompts` (List[SunoPrompt]): List of parsed SunoPrompt objects
- **Returns:** `QueueEntry` - Created queue entry with unique ID
- **Raises:** `QueueValidationError` - If validation fails
- **Description:** Adds a new queue entry if sufficient prompts remain

##### `remove_queue_entry()`
```python
def remove_queue_entry(self, queue_id: str) -> bool
```
- **Parameters:**
  - `queue_id` (str): Unique identifier of the queue entry
- **Returns:** `bool` - True if entry was removed, False if not found
- **Description:** Removes a queue entry by its ID

##### `get_queue()`
```python
def get_queue(self, queue_id: str) -> Optional[QueueEntry]
```
- **Parameters:**
  - `queue_id` (str): Unique identifier of the queue entry
- **Returns:** `Optional[QueueEntry]` - Queue entry or None if not found
- **Description:** Retrieves a specific queue entry by ID

##### `get_all_queues()`
```python
def get_all_queues(self) -> List[QueueEntry]
```
- **Returns:** `List[QueueEntry]` - All queue entries sorted by creation order
- **Description:** Returns all queue entries in chronological order

##### `get_pending_queues()`
```python
def get_pending_queues(self) -> List[QueueEntry]
```
- **Returns:** `List[QueueEntry]` - Queue entries with "pending" or "in_progress" status
- **Description:** Returns queue entries that are not completed or failed

##### `update_queue_progress()`
```python
def update_queue_progress(
    self,
    queue_id: str,
    completed_count: Optional[int] = None,
    status: Optional[str] = None,
) -> bool
```
- **Parameters:**
  - `queue_id` (str): Unique identifier of the queue entry
  - `completed_count` (Optional[int]): Number of completed songs (capped at total)
  - `status` (Optional[str]): New status for the queue entry
- **Returns:** `bool` - True if update was successful, False if queue not found
- **Description:** Updates progress metrics and status for a queue entry

#### Properties

##### `available_prompt_slots`
```python
@property
def available_prompt_slots(self) -> int
```
- **Returns:** `int` - Number of prompts still unassigned to queues
- **Description:** Calculates remaining prompt capacity

#### Validation Methods

##### `validate_total_prompts()`
```python
def validate_total_prompts(self, requested_total: int) -> bool
```
- **Parameters:**
  - `requested_total` (int): Total number of prompts being requested
- **Returns:** `bool` - True if enough prompts remain, False otherwise
- **Description:** Verifies sufficient prompt availability before queue creation

### Exceptions

#### `QueueValidationError`
Raised when queue state violates prompt limits or input rules.

### Usage Example

```python
from src.core.queue_manager import QueueManager
from src.utils.prompt_parser import SunoPrompt

# Initialize queue manager
queue_manager = QueueManager()

# Create prompts
prompts = [
    SunoPrompt(title="Song 1", lyrics="Lyrics 1", style="Pop"),
    SunoPrompt(title="Song 2", lyrics="Lyrics 2", style="Rock"),
]

# Add queue entry
entry = queue_manager.add_queue_entry(
    account_name="user1",
    total_songs=2,
    songs_per_batch=1,
    prompts=prompts
)

# Update progress
queue_manager.update_queue_progress(
    queue_id=entry.id,
    completed_count=1,
    status="in_progress"
)
```

---

## Data Models

### QueueEntry

Data model representing a song creation queue entry.

#### Properties
- `id` (str): Unique identifier (UUID4)
- `account_name` (str): Associated account name
- `total_songs` (int): Total songs to create
- `songs_per_batch` (int): Songs per batch
- `completed_count` (int): Number of completed songs
- `status` (str): Queue status ("pending", "in_progress", "completed", "failed")
- `prompts_range` (tuple): Start and end indices in prompts list
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

#### Methods
- `to_dict()`: Convert to dictionary representation
- `from_dict()`: Create instance from dictionary

---

## Integration Patterns

### Error Handling
All methods use proper exception handling with specific error types:
- `QueueValidationError` for validation failures
- File I/O errors are logged and handled gracefully

### State Persistence
- Queue state is automatically persisted to disk after modifications
- Atomic writes ensure data consistency
- Version compatibility is maintained for future upgrades

### Thread Safety
- Queue manager is not thread-safe by design
- External synchronization is required for concurrent access
- State modifications should be serialized

---

## Configuration

### Environment Variables
- `QUEUE_STATE_FILE`: Path to queue state persistence file (default: from config)

### Dependencies
- `config.settings`: Configuration management
- `src.models`: Data models (QueueEntry)
- `src.utils`: Utility functions (atomic_write_json, load_json, logger)
- `src.utils.prompt_parser`: SunoPrompt class

---

## Performance Considerations

### Memory Usage
- Queue entries are stored in memory for fast access
- Large queue volumes may require memory optimization
- Consider pagination for very large queue lists

### Disk I/O
- State is persisted after each modification
- Atomic writes ensure data integrity but may impact performance
- Consider batching updates for high-frequency operations

---

## Testing

### Unit Tests
- `tests/test_queue_manager.py`: Comprehensive test suite
- Tests cover all public methods and edge cases
- Mock objects used for isolated testing

### Integration Tests
- `tests/test_queue_workflow.py`: End-to-end queue workflows
- Tests integration with other core components

---

## Future Enhancements

### Planned Features
- Thread-safe operations for concurrent access
- Queue prioritization and dependency management
- Advanced scheduling and retry mechanisms
- Performance monitoring and analytics

### API Compatibility
- Breaking changes will increment version number
- Backward compatibility maintained when possible
- Migration utilities provided for major version updates