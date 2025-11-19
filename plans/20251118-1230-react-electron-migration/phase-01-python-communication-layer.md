# Phase 1: Python Communication Layer

## Context
**Parent Plan:** [plan.md](plan.md)
**Dependencies:** Existing Python backend managers
**Duration:** 1-2 weeks
**Priority:** High

## Overview

Add stdin/stdout communication layer to existing Python backend with minimal changes to preserve all current functionality while enabling React + Electron integration.

## Key Insights

- Python backend architecture is well-designed with Clean Architecture principles
- Managers are already modular and can be easily wrapped with communication layer
- Existing progress callback system can be adapted for IPC communication
- Chrome automation and Selenium integration should remain untouched

## Requirements

### Functional Requirements
1. **Stdin Communication:** Accept JSON commands from Electron via stdin
2. **Stdout Responses:** Send structured JSON responses via stdout
3. **Progress Events:** Real-time progress updates for long-running operations
4. **Error Handling:** Robust error propagation with detailed error messages
5. **Command Routing:** Route commands to appropriate manager methods
6. **State Persistence:** Maintain all existing data persistence mechanisms

### Technical Requirements
1. **Type Safety:** Structured command/response interfaces
2. **Thread Safety:** Handle concurrent operations safely
3. **Performance:** Minimal overhead for communication layer
4. **Backward Compatibility:** Preserve all existing functionality
5. **Debugging:** Comprehensive logging for communication

## Architecture

### Communication Protocol

```python
# Command Structure
{
    "id": "unique-command-id",
    "type": "CREATE_ACCOUNT",
    "payload": {
        "name": "account_name",
        "email": "user@example.com"
    },
    "timestamp": 1637200000000
}

# Response Structure
{
    "id": "unique-command-id",
    "type": "CREATE_ACCOUNT_RESPONSE",
    "success": true,
    "data": {
        "name": "account_name",
        "email": "user@example.com",
        "created_at": "2025-11-18T12:30:00"
    },
    "timestamp": 1637200000100
}

# Progress Event Structure
{
    "id": "progress-event-id",
    "type": "QUEUE_PROGRESS",
    "payload": {
        "queue_id": "queue-123",
        "progress": 45,
        "status": "in_progress",
        "current_song": "Song Title",
        "message": "Processing batch 2/5"
    },
    "timestamp": 1637200000200
}
```

### Command Router Architecture

```python
class CommandRouter:
    def __init__(self):
        self.managers = {
            'account': AccountManager(),
            'queue': QueueManager(),
            'download': DownloadManager(),
            'session': SessionManager(),
            'batch_creator': BatchSongCreator(),
            'history': SongCreationHistoryManager()
        }

    def process_command(self, command: dict) -> dict:
        """Route command to appropriate manager and return response"""
        command_type = command.get('type')
        payload = command.get('payload', {})

        if command_type == 'GET_ACCOUNTS':
            return self._handle_get_accounts(payload)
        elif command_type == 'CREATE_ACCOUNT':
            return self._handle_create_account(payload)
        # ... other commands
```

## Related Code Files

### Files to Modify
- `app.py` - Add stdin communication loop
- `src/core/` - Add command wrapper methods
- `src/models/data_models.py` - Add communication data models

### Files to Create
- `backend/communication_layer.py` - Main communication logic
- `backend/command_router.py` - Command routing and processing
- `backend/types.py` - Communication data structures

## Implementation Steps

### Step 1: Setup Communication Foundation (Day 1-2)
1. **Create communication layer structure**
   ```bash
   mkdir -p backend/communication
   touch backend/communication/__init__.py
   touch backend/communication/command_router.py
   touch backend/communication/message_handler.py
   touch backend/communication/types.py
   ```

2. **Define communication data structures**
   ```python
   # backend/communication/types.py
   from dataclasses import dataclass
   from typing import Any, Optional
   import time

   @dataclass
   class Command:
       id: str
       type: str
       payload: Optional[dict] = None
       timestamp: int = int(time.time())

   @dataclass
   class Response:
       id: str
       type: str
       success: bool
       data: Optional[Any] = None
       error: Optional[str] = None
       timestamp: int = int(time.time())
   ```

3. **Create main communication entry point**
   ```python
   # backend/main.py
   import sys
   import json
   from communication.command_router import CommandRouter

   def main():
       router = CommandRouter()
       print("Backend ready for stdin communication", file=sys.stderr)

       while True:
           try:
               line = sys.stdin.readline()
               if not line:
                   break

               command_data = json.loads(line.strip())
               response = router.process_command(command_data)

               sys.stdout.write(json.dumps(response) + '\n')
               sys.stdout.flush()

           except Exception as e:
               error_response = {
                   "success": False,
                   "error": str(e),
                   "timestamp": int(time.time())
               }
               sys.stdout.write(json.dumps(error_response) + '\n')
               sys.stdout.flush()

   if __name__ == "__main__":
       main()
   ```

### Step 2: Implement Command Router (Day 3-4)
1. **Create command router with manager integration**
   ```python
   # backend/communication/command_router.py
   from typing import Dict, Any, List
   import uuid
   import time

   from src.core.account_manager import AccountManager
   from src.core.queue_manager import QueueManager
   from src.core.download_manager import DownloadManager
   from src.core.session_manager import SessionManager
   from src.core.batch_song_creator import BatchSongCreator
   from src.core.song_creation_history_manager import SongCreationHistoryManager
   from .types import Command, Response

   class CommandRouter:
       def __init__(self):
           self.account_manager = AccountManager()
           self.queue_manager = QueueManager()
           self.download_manager = DownloadManager()
           self.session_manager = SessionManager()
           self.batch_song_creator = BatchSongCreator()
           self.history_manager = SongCreationHistoryManager()

           self.progress_callbacks = {}

       def process_command(self, command_data: dict) -> dict:
           """Process incoming command and return response"""
           command = Command(**command_data)

           try:
               if command.type == 'GET_ACCOUNTS':
                   return self._handle_get_accounts(command)
               elif command.type == 'CREATE_ACCOUNT':
                   return self._handle_create_account(command)
               elif command.type == 'DELETE_ACCOUNT':
                   return self._handle_delete_account(command)
               elif command.type == 'GET_QUEUES':
                   return self._handle_get_queues(command)
               elif command.type == 'CREATE_QUEUE':
                   return self._handle_create_queue(command)
               elif command.type == 'START_QUEUE':
                   return self._handle_start_queue(command)
               elif command.type == 'GET_QUEUE_PROGRESS':
                   return self._handle_get_queue_progress(command)
               elif command.type == 'START_DOWNLOAD':
                   return self._handle_start_download(command)
               elif command.type == 'GET_DOWNLOAD_PROGRESS':
                   return self._handle_get_download_progress(command)
               elif command.type == 'GET_HISTORY':
                   return self._handle_get_history(command)
               else:
                   return self._create_error_response(
                       command.id,
                       f"Unknown command type: {command.type}"
                   )
           except Exception as e:
               return self._create_error_response(
                   command.id,
                   f"Error processing command: {str(e)}"
               )
   ```

2. **Implement manager command handlers**
   ```python
   # Account management handlers
   def _handle_get_accounts(self, command: Command) -> dict:
       accounts = self.account_manager.get_all_accounts()
       return self._create_success_response(
           command.id,
           [self._account_to_dict(acc) for acc in accounts]
       )

   def _handle_create_account(self, command: Command) -> dict:
       payload = command.payload
       name = payload.get('name')
       email = payload.get('email')

       if not name:
           return self._create_error_response(command.id, "Account name is required")

       success = self.account_manager.add_account(name, email)
       if success:
           account = self.account_manager.get_account(name)
           return self._create_success_response(command.id, self._account_to_dict(account))
       else:
           return self._create_error_response(command.id, "Failed to create account")

   # Queue management handlers
   def _handle_create_queue(self, command: Command) -> dict:
       payload = command.payload

       # Convert prompts from dict to SunoPrompt objects
       prompts_data = payload.get('prompts', [])
       prompts = []
       for prompt_data in prompts_data:
           from src.utils.prompt_parser import SunoPrompt
           prompt = SunoPrompt(
               title=prompt_data['title'],
               lyrics=prompt_data['lyrics'],
               style=prompt_data['style']
           )
           prompts.append(prompt)

       queue_entry = self.queue_manager.add_queue_entry(
           account_name=payload.get('account_name'),
           total_songs=payload.get('total_songs'),
           songs_per_batch=payload.get('songs_per_batch'),
           prompts=prompts
       )

       return self._create_success_response(command.id, self._queue_entry_to_dict(queue_entry))
   ```

### Step 3: Progress Callback System (Day 5-6)
1. **Implement progress callback wrapper**
   ```python
   # backend/communication/progress_manager.py
   import threading
   import json
   import sys
   from typing import Dict, Callable, Any

   class ProgressManager:
       def __init__(self):
           self.active_operations: Dict[str, threading.Event] = {}
           self.progress_lock = threading.Lock()

       def register_operation(self, operation_id: str) -> threading.Event:
           """Register a new operation for progress tracking"""
           with self.progress_lock:
               event = threading.Event()
               self.active_operations[operation_id] = event
           return event

       def create_progress_callback(self, operation_id: str) -> Callable:
           """Create progress callback for an operation"""
           def progress_callback(message: str, progress: int, song_id: str = None, status: str = None, title: str = None):
               progress_data = {
                   "id": "progress-event",
                   "type": "PROGRESS_UPDATE",
                   "payload": {
                       "operation_id": operation_id,
                       "message": message,
                       "progress": progress,
                       "song_id": song_id,
                       "status": status,
                       "title": title
                   },
                   "timestamp": int(time.time())
               }

               # Send progress event to stdout
               sys.stdout.write(json.dumps(progress_data) + '\n')
               sys.stdout.flush()

           return progress_callback

       def complete_operation(self, operation_id: str):
           """Mark operation as complete"""
           with self.progress_lock:
               if operation_id in self.active_operations:
                   self.active_operations[operation_id].set()
                   del self.active_operations[operation_id]
   ```

2. **Integrate progress callbacks with batch operations**
   ```python
   # In command router
   def _handle_start_queue(self, command: Command) -> dict:
       payload = command.payload
       queue_ids = payload.get('queue_ids', [])

       # Create progress callback
       operation_id = str(uuid.uuid4())
       progress_callback = self.progress_manager.create_progress_callback(operation_id)

       # Start queue execution in background thread
       def execute_queues():
           try:
               self.batch_song_creator.execute_queues(
                   queue_ids,
                   progress_callback=progress_callback
               )
           except Exception as e:
               error_data = {
                   "id": "progress-event",
                   "type": "ERROR_UPDATE",
                   "payload": {
                       "operation_id": operation_id,
                       "error": str(e)
                   }
               }
               sys.stdout.write(json.dumps(error_data) + '\n')
               sys.stdout.flush()
           finally:
               self.progress_manager.complete_operation(operation_id)

       thread = threading.Thread(target=execute_queues, daemon=True)
       thread.start()

       return self._create_success_response(command.id, {
           "operation_id": operation_id,
           "queue_ids": queue_ids,
           "status": "started"
       })
   ```

### Step 4: Testing and Validation (Day 7-10)
1. **Create comprehensive test suite**
   ```python
   # tests/test_communication_layer.py
   import json
   import subprocess
   import time
   from pathlib import Path

   class TestCommunicationLayer:
       def test_account_creation(self):
           """Test account creation via stdin communication"""

           # Start Python backend process
           process = subprocess.Popen(
               ['python', 'backend/main.py'],
               stdin=subprocess.PIPE,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               text=True
           )

           # Send create account command
           command = {
               "id": "test-1",
               "type": "CREATE_ACCOUNT",
               "payload": {
                   "name": "test_account",
                   "email": "test@example.com"
               }
           }

           process.stdin.write(json.dumps(command) + '\n')
           process.stdin.flush()

           # Read response
           response_line = process.stdout.readline()
           response = json.loads(response_line.strip())

           assert response["success"] == True
           assert response["data"]["name"] == "test_account"

           process.terminate()

       def test_queue_creation(self):
           """Test queue creation via stdin communication"""
           # Similar test pattern for queue operations
           pass
   ```

2. **Create integration test with mock Electron**
   ```python
   # tests/test_electron_integration.py
   import subprocess
   import json
   import threading
   import time

   def test_full_workflow():
       """Test complete workflow from account creation to queue execution"""

       # Start backend
       backend = subprocess.Popen(['python', 'backend/main.py'],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

       # Test commands
       commands = [
           {"id": "1", "type": "CREATE_ACCOUNT", "payload": {"name": "test", "email": "test@test.com"}},
           {"id": "2", "type": "GET_ACCOUNTS", "payload": {}},
           {"id": "3", "type": "CREATE_QUEUE", "payload": {"account_name": "test", "total_songs": 5, "songs_per_batch": 2, "prompts": [{"title": "Test", "lyrics": "Test lyrics", "style": "Pop"}]}}
       ]

       for cmd in commands:
           backend.stdin.write(json.dumps(cmd) + '\n')
           backend.stdin.flush()

           response = json.loads(backend.stdout.readline().strip())
           print(f"Response to {cmd['type']}: {response}")

           assert response["success"] == True

       backend.terminate()
   ```

## Todo List

- [ ] Create communication layer directory structure
- [ ] Define communication data structures and types
- [ ] Implement main stdin communication loop
- [ ] Create command router with manager integration
- [ ] Implement progress callback system
- [ ] Add comprehensive error handling
- [ ] Create test suite for communication layer
- [ ] Integration testing with mock Electron
- [ ] Performance testing and optimization
- [ ] Documentation for communication protocol

## Success Criteria

- ✅ All existing manager methods accessible via stdin communication
- ✅ Real-time progress updates working for long-running operations
- ✅ Error handling and propagation working correctly
- ✅ Thread-safe operations
- ✅ Comprehensive test coverage
- ✅ Performance overhead < 5% compared to direct method calls
- ✅ Backward compatibility maintained

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Communication overhead** | Low | Low | Efficient JSON serialization, minimize data transfer |
| **Thread safety issues** | Medium | High | Proper locking mechanisms, thread-safe data structures |
| **Progress callback complexity** | Medium | Medium | Clean abstraction layer, comprehensive testing |
| **Manager integration bugs** | Low | High | Thorough testing of all command handlers |

## Security Considerations

1. **Input Validation:** Validate all incoming JSON commands
2. **Error Information:** Avoid exposing sensitive data in error messages
3. **Resource Limits:** Implement timeouts and memory usage limits
4. **Access Control:** Command-based access control if needed

## Next Steps

1. **Phase 2 Setup:** Begin Electron main process development
2. **TypeScript Integration:** Create type definitions for communication protocol
3. **IPC Bridge Development:** Implement Electron IPC bridge
4. **Testing Setup:** Create integration testing framework

---

*This phase establishes the foundation for React + Electron integration while preserving all existing Python backend functionality.*