"""
Message Handler - Base class for handling stdin/stdout communication
"""
import sys
import json
import threading
from typing import Callable, Optional, Dict, Any
from .types import Command, Response, ProgressEvent, ProgressEventTypes


class MessageHandler:
    """Base message handler for stdin/stdout communication"""

    def __init__(self):
        self.progress_callbacks: Dict[str, Callable] = {}
        self.message_lock = threading.Lock()

    def send_response(self, command_id: str, response_type: str,
                     success: bool, data: Any = None, error: str = None):
        """Send response to stdout"""
        response = Response(
            id=command_id,
            type=response_type,
            success=success,
            data=data,
            error=error
        )

        with self.message_lock:
            sys.stdout.write(json.dumps(response.to_dict()) + '\n')
            sys.stdout.flush()

    def send_progress_event(self, payload: Dict[str, Any],
                           event_type: str = ProgressEventTypes.QUEUE_PROGRESS):
        """Send progress event to stdout"""
        event = ProgressEvent(
            id="progress-event",
            type=event_type,
            payload=payload
        )

        with self.message_lock:
            sys.stdout.write(json.dumps(event.to_dict()) + '\n')
            sys.stdout.flush()

    def parse_command(self, line: str) -> Optional[Command]:
        """Parse incoming command from stdin"""
        try:
            data = json.loads(line.strip())
            return Command(**data)
        except json.JSONDecodeError as e:
            error_response = Response(
                id="parse-error",
                type="PARSE_ERROR",
                success=False,
                error=f"Invalid JSON: {str(e)}"
            )

            with self.message_lock:
                sys.stdout.write(json.dumps(error_response.to_dict()) + '\n')
                sys.stdout.flush()

            return None
        except Exception as e:
            error_response = Response(
                id="parse-error",
                type="PARSE_ERROR",
                success=False,
                error=f"Parse error: {str(e)}"
            )

            with self.message_lock:
                sys.stdout.write(json.dumps(error_response.to_dict()) + '\n')
                sys.stdout.flush()

            return None

    def register_progress_callback(self, operation_id: str, callback: Callable):
        """Register progress callback for an operation"""
        self.progress_callbacks[operation_id] = callback

    def unregister_progress_callback(self, operation_id: str):
        """Unregister progress callback"""
        if operation_id in self.progress_callbacks:
            del self.progress_callbacks[operation_id]


# Add serialization methods to data classes
def _add_to_dict_methods():
    """Add to_dict methods to data classes"""

    def command_to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'payload': self.payload,
            'timestamp': self.timestamp
        }

    def response_to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'timestamp': self.timestamp
        }

    def progress_event_to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'payload': self.payload,
            'timestamp': self.timestamp
        }

    Command.to_dict = command_to_dict
    Response.to_dict = response_to_dict
    ProgressEvent.to_dict = progress_event_to_dict


_add_to_dict_methods()