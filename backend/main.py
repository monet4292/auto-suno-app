"""
Main Backend Process - Entry point for stdin/stdout communication
"""
import sys
import json
import signal
import threading
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.account_manager import AccountManager
from src.core.queue_manager import QueueManager
from src.core.download_manager import DownloadManager
from src.core.session_manager import SessionManager
from src.core.batch_song_creator import BatchSongCreator
from src.core.song_creation_history_manager import SongCreationHistoryManager

from backend.communication.command_router import CommandRouter
from src.utils import logger


class BackendProcess:
    """Main backend process for communication with Electron"""

    def __init__(self):
        self.router = CommandRouter()
        self.running = True
        self.threads = []

        # Initialize managers
        self._initialize_managers()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _initialize_managers(self):
        """Initialize all managers"""
        try:
            # Create manager instances
            account_manager = AccountManager()
            queue_manager = QueueManager()
            download_manager = DownloadManager()
            session_manager = SessionManager()
            # Create default profile path for BatchSongCreator
            default_profile_path = Path.home() / ".suno" / "default_profile"
            default_profile_path.mkdir(parents=True, exist_ok=True)
            batch_song_creator = BatchSongCreator(default_profile_path)
            history_manager = SongCreationHistoryManager()

            # Register managers with router
            self.router.register_managers(
                account=account_manager,
                queue=queue_manager,
                download=download_manager,
                session=session_manager,
                batch_song_creator=batch_song_creator,
                history=history_manager
            )

            logger.info("All managers initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize managers: {e}")
            sys.exit(1)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def _send_ready_message(self):
        """Send ready message to stderr for Electron to detect"""
        ready_msg = {
            "type": "BACKEND_READY",
            "timestamp": int(time.time()),
            "version": "1.0.0"
        }
        sys.stderr.write(json.dumps(ready_msg) + '\n')
        sys.stderr.flush()

    def run(self):
        """Main communication loop"""
        logger.info("Backend process starting...")
        self._send_ready_message()

        try:
            while self.running:
                try:
                    # Read command from stdin
                    line = sys.stdin.readline()
                    if not line:
                        # EOF received
                        logger.info("EOF received, shutting down...")
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # Parse command
                    try:
                        command_data = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON received: {e}")
                        continue

                    # Process command
                    response = self.router.process_command(command_data)
                    if response:
                        # Send response to stdout
                        sys.stdout.write(json.dumps(response) + '\n')
                        sys.stdout.flush()

                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    # Send error response
                    error_response = {
                        "id": "system-error",
                        "type": "ERROR_RESPONSE",
                        "success": False,
                        "error": str(e),
                        "timestamp": int(time.time())
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        self.running = False

        # Wait for any active threads to complete
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5.0)

        logger.info("Backend process shutdown complete")


def main():
    """Entry point"""
    backend = BackendProcess()
    backend.run()


if __name__ == "__main__":
    main()