"""
Progress Manager - Handles progress tracking and callbacks for long-running operations
"""
import threading
import time
import uuid
from typing import Dict, Callable, Any, Optional
from .message_handler import MessageHandler, ProgressEventTypes


class ProgressManager:
    """Manages progress tracking for long-running operations"""

    def __init__(self):
        self.active_operations: Dict[str, threading.Event] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
        self.progress_lock = threading.Lock()

    def register_operation(self, operation_id: str) -> threading.Event:
        """Register a new operation for progress tracking"""
        with self.progress_lock:
            event = threading.Event()
            self.active_operations[operation_id] = event
        return event

    def create_progress_callback(self, operation_id: str,
                               message_handler: MessageHandler) -> Callable:
        """Create progress callback for an operation"""
        def progress_callback(message: str, progress: int = 0,
                            song_id: Optional[str] = None,
                            status: Optional[str] = None,
                            title: Optional[str] = None,
                            queue_id: Optional[str] = None):
            """Progress callback function"""
            progress_data = {
                "id": "progress-event",
                "type": ProgressEventTypes.SONG_CREATION_PROGRESS,
                "payload": {
                    "operation_id": operation_id,
                    "message": message,
                    "progress": progress,
                    "song_id": song_id,
                    "status": status,
                    "title": title,
                    "queue_id": queue_id,
                    "timestamp": int(time.time())
                }
            }

            # Send progress event via message handler
            message_handler.send_progress_event(
                progress_data["payload"],
                ProgressEventTypes.SONG_CREATION_PROGRESS
            )

        return progress_callback

    def create_queue_progress_callback(self, operation_id: str,
                                     message_handler: MessageHandler) -> Callable:
        """Create progress callback for queue operations"""
        def queue_progress_callback(queue_id: str, completed: int, total: int,
                                  status: str, message: str):
            """Queue progress callback function"""
            progress_data = {
                "id": "progress-event",
                "type": ProgressEventTypes.QUEUE_PROGRESS,
                "payload": {
                    "operation_id": operation_id,
                    "queue_id": queue_id,
                    "completed": completed,
                    "total": total,
                    "progress": int((completed / total) * 100) if total > 0 else 0,
                    "status": status,
                    "message": message,
                    "timestamp": int(time.time())
                }
            }

            message_handler.send_progress_event(
                progress_data["payload"],
                ProgressEventTypes.QUEUE_PROGRESS
            )

        return queue_progress_callback

    def create_download_progress_callback(self, operation_id: str,
                                        message_handler: MessageHandler) -> Callable:
        """Create progress callback for download operations"""
        def download_progress_callback(file_name: str, downloaded: int, total: int,
                                     speed: float = 0):
            """Download progress callback function"""
            progress_data = {
                "id": "progress-event",
                "type": ProgressEventTypes.DOWNLOAD_PROGRESS,
                "payload": {
                    "operation_id": operation_id,
                    "file_name": file_name,
                    "downloaded": downloaded,
                    "total": total,
                    "progress": int((downloaded / total) * 100) if total > 0 else 0,
                    "speed": speed,
                    "timestamp": int(time.time())
                }
            }

            message_handler.send_progress_event(
                progress_data["payload"],
                ProgressEventTypes.DOWNLOAD_PROGRESS
            )

        return download_progress_callback

    def complete_operation(self, operation_id: str):
        """Mark operation as complete"""
        with self.progress_lock:
            if operation_id in self.active_operations:
                self.active_operations[operation_id].set()
                del self.active_operations[operation_id]

    def fail_operation(self, operation_id: str, error: str,
                      message_handler: MessageHandler):
        """Mark operation as failed"""
        error_data = {
            "id": "progress-event",
            "type": ProgressEventTypes.ERROR_UPDATE,
            "payload": {
                "operation_id": operation_id,
                "error": error,
                "timestamp": int(time.time())
            }
        }

        message_handler.send_progress_event(
            error_data["payload"],
            ProgressEventTypes.ERROR_UPDATE
        )

        self.complete_operation(operation_id)

    def is_operation_active(self, operation_id: str) -> bool:
        """Check if operation is still active"""
        with self.progress_lock:
            return operation_id in self.active_operations

    def get_active_operations(self) -> Dict[str, Dict[str, Any]]:
        """Get all active operations"""
        with self.progress_lock:
            return {
                op_id: {"active": True}
                for op_id in self.active_operations.keys()
            }

    def wait_for_operation(self, operation_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for operation to complete"""
        with self.progress_lock:
            event = self.active_operations.get(operation_id)

        if event:
            return event.wait(timeout)
        return False

    def generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return str(uuid.uuid4())