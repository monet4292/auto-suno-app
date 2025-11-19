"""
Communication Data Types and Structures
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
import time
import uuid


@dataclass
class Command:
    """Command structure for stdin communication"""
    id: str
    type: str
    payload: Optional[Dict[str, Any]] = None
    timestamp: int = field(default_factory=lambda: int(time.time()))

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Response:
    """Response structure for stdout communication"""
    id: str
    type: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time()))


@dataclass
class ProgressEvent:
    """Progress event structure for real-time updates"""
    id: str
    type: str
    payload: Dict[str, Any]
    timestamp: int = field(default_factory=lambda: int(time.time()))


# Command Types
class CommandTypes:
    """All supported command types"""

    # Account Management
    GET_ACCOUNTS = "GET_ACCOUNTS"
    CREATE_ACCOUNT = "CREATE_ACCOUNT"
    UPDATE_ACCOUNT = "UPDATE_ACCOUNT"
    RENAME_ACCOUNT = "RENAME_ACCOUNT"
    DELETE_ACCOUNT = "DELETE_ACCOUNT"
    GET_ACCOUNT_PROFILE_PATH = "GET_ACCOUNT_PROFILE_PATH"

    # Queue Management
    GET_QUEUES = "GET_QUEUES"
    CREATE_QUEUE = "CREATE_QUEUE"
    REMOVE_QUEUE = "REMOVE_QUEUE"
    UPDATE_QUEUE_PROGRESS = "UPDATE_QUEUE_PROGRESS"
    VALIDATE_PROMPTS = "VALIDATE_PROMPTS"
    CLEAR_QUEUES = "CLEAR_QUEUES"

    # Session Management
    LAUNCH_BROWSER = "LAUNCH_BROWSER"
    GET_SESSION_TOKEN = "GET_SESSION_TOKEN"
    VERIFY_SESSION = "VERIFY_SESSION"

    # Download Management
    GET_DOWNLOAD_HISTORY = "GET_DOWNLOAD_HISTORY"
    FETCH_CLIPS = "FETCH_CLIPS"
    GET_NEW_CLIPS = "GET_NEW_CLIPS"
    DOWNLOAD_CLIP = "DOWNLOAD_CLIP"
    BATCH_DOWNLOAD = "BATCH_DOWNLOAD"
    CLEAR_DOWNLOAD_HISTORY = "CLEAR_DOWNLOAD_HISTORY"

    # Batch Song Creation
    CREATE_SONGS_BATCH = "CREATE_SONGS_BATCH"
    START_QUEUE_EXECUTION = "START_QUEUE_EXECUTION"

    # History Management
    GET_CREATION_HISTORY = "GET_CREATION_HISTORY"
    ADD_CREATION_RECORD = "ADD_CREATION_RECORD"
    EXPORT_HISTORY_TO_CSV = "EXPORT_HISTORY_TO_CSV"
    SEARCH_HISTORY = "SEARCH_HISTORY"


# Response Types
class ResponseTypes:
    """Response types for each command"""

    # Account Management Responses
    GET_ACCOUNTS_RESPONSE = "GET_ACCOUNTS_RESPONSE"
    CREATE_ACCOUNT_RESPONSE = "CREATE_ACCOUNT_RESPONSE"
    UPDATE_ACCOUNT_RESPONSE = "UPDATE_ACCOUNT_RESPONSE"
    RENAME_ACCOUNT_RESPONSE = "RENAME_ACCOUNT_RESPONSE"
    DELETE_ACCOUNT_RESPONSE = "DELETE_ACCOUNT_RESPONSE"
    GET_ACCOUNT_PROFILE_PATH_RESPONSE = "GET_ACCOUNT_PROFILE_PATH_RESPONSE"

    # Queue Management Responses
    GET_QUEUES_RESPONSE = "GET_QUEUES_RESPONSE"
    CREATE_QUEUE_RESPONSE = "CREATE_QUEUE_RESPONSE"
    REMOVE_QUEUE_RESPONSE = "REMOVE_QUEUE_RESPONSE"
    UPDATE_QUEUE_PROGRESS_RESPONSE = "UPDATE_QUEUE_PROGRESS_RESPONSE"
    VALIDATE_PROMPTS_RESPONSE = "VALIDATE_PROMPTS_RESPONSE"
    CLEAR_QUEUES_RESPONSE = "CLEAR_QUEUES_RESPONSE"

    # Session Management Responses
    LAUNCH_BROWSER_RESPONSE = "LAUNCH_BROWSER_RESPONSE"
    GET_SESSION_TOKEN_RESPONSE = "GET_SESSION_TOKEN_RESPONSE"
    VERIFY_SESSION_RESPONSE = "VERIFY_SESSION_RESPONSE"

    # Download Management Responses
    GET_DOWNLOAD_HISTORY_RESPONSE = "GET_DOWNLOAD_HISTORY_RESPONSE"
    FETCH_CLIPS_RESPONSE = "FETCH_CLIPS_RESPONSE"
    GET_NEW_CLIPS_RESPONSE = "GET_NEW_CLIPS_RESPONSE"
    DOWNLOAD_CLIP_RESPONSE = "DOWNLOAD_CLIP_RESPONSE"
    BATCH_DOWNLOAD_RESPONSE = "BATCH_DOWNLOAD_RESPONSE"
    CLEAR_DOWNLOAD_HISTORY_RESPONSE = "CLEAR_DOWNLOAD_HISTORY_RESPONSE"

    # Batch Song Creation Responses
    CREATE_SONGS_BATCH_RESPONSE = "CREATE_SONGS_BATCH_RESPONSE"
    START_QUEUE_EXECUTION_RESPONSE = "START_QUEUE_EXECUTION_RESPONSE"

    # History Management Responses
    GET_CREATION_HISTORY_RESPONSE = "GET_CREATION_HISTORY_RESPONSE"
    ADD_CREATION_RECORD_RESPONSE = "ADD_CREATION_RECORD_RESPONSE"
    EXPORT_HISTORY_TO_CSV_RESPONSE = "EXPORT_HISTORY_TO_CSV_RESPONSE"
    SEARCH_HISTORY_RESPONSE = "SEARCH_HISTORY_RESPONSE"


# Progress Event Types
class ProgressEventTypes:
    """Progress event types for real-time updates"""

    # Queue Progress
    QUEUE_PROGRESS = "QUEUE_PROGRESS"
    BATCH_PROGRESS = "BATCH_PROGRESS"
    SONG_PROGRESS = "SONG_PROGRESS"

    # Download Progress
    DOWNLOAD_PROGRESS = "DOWNLOAD_PROGRESS"
    BATCH_DOWNLOAD_PROGRESS = "BATCH_DOWNLOAD_PROGRESS"

    # Song Creation Progress
    SONG_CREATION_PROGRESS = "SONG_CREATION_PROGRESS"

    # Error Events
    ERROR_UPDATE = "ERROR_UPDATE"
    WARNING_UPDATE = "WARNING_UPDATE"


# Error Codes
class ErrorCodes:
    """Standard error codes"""

    # General Errors
    UNKNOWN_COMMAND = "UNKNOWN_COMMAND"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Account Errors
    ACCOUNT_NOT_FOUND = "ACCOUNT_NOT_FOUND"
    ACCOUNT_ALREADY_EXISTS = "ACCOUNT_ALREADY_EXISTS"
    ACCOUNT_CREATION_FAILED = "ACCOUNT_CREATION_FAILED"

    # Queue Errors
    QUEUE_NOT_FOUND = "QUEUE_NOT_FOUND"
    INSUFFICIENT_PROMPTS = "INSUFFICIENT_PROMPTS"
    INVALID_QUEUE_PARAMETERS = "INVALID_QUEUE_PARAMETERS"

    # Session Errors
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    BROWSER_LAUNCH_FAILED = "BROWSER_LAUNCH_FAILED"
    PROFILE_LOCKED = "PROFILE_LOCKED"

    # Download Errors
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    CLIP_NOT_FOUND = "CLIP_NOT_FOUND"

    # Song Creation Errors
    SONG_CREATION_FAILED = "SONG_CREATION_FAILED"
    BATCH_CREATION_FAILED = "BATCH_CREATION_FAILED"