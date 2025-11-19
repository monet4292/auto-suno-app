"""
Test Communication Layer - Comprehensive test suite for stdin/stdout communication
"""
import json
import subprocess
import time
import tempfile
import os
from pathlib import Path
import threading
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.communication.command_router import CommandRouter
from backend.communication.types import Command, Response, ProgressEvent
from backend.communication.progress_manager import ProgressManager
from src.core.account_manager import AccountManager
from src.core.queue_manager import QueueManager
from src.models import Account


class TestCommunicationLayer:
    """Test suite for communication layer functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock config paths
        self.config_patcher = patch('config.settings.ACCOUNTS_FILE',
                                   Path(self.temp_dir) / 'accounts.json')
        self.config_patcher.start()

        self.config_patcher2 = patch('config.settings.QUEUE_STATE_FILE',
                                    Path(self.temp_dir) / 'queue_state.json')
        self.config_patcher2.start()

        # Create test managers
        self.account_manager = AccountManager()
        self.queue_manager = QueueManager()

        # Create command router
        self.router = CommandRouter()
        self.router.register_managers(
            account=self.account_manager,
            queue=self.queue_manager
        )

    def teardown_method(self):
        """Cleanup test environment"""
        self.config_patcher.stop()
        self.config_patcher2.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_account_creation(self):
        """Test account creation via command router"""
        command = {
            "id": "test-1",
            "type": "CREATE_ACCOUNT",
            "payload": {
                "name": "test_account",
                "email": "test@example.com"
            }
        }

        response = self.router.process_command(command)

        assert response["success"] == True
        assert response["data"]["name"] == "test_account"
        assert response["data"]["email"] == "test@example.com"
        assert response["type"] == "CREATE_ACCOUNT_RESPONSE"

        # Verify account was actually created
        account = self.account_manager.get_account("test_account")
        assert account is not None
        assert account.email == "test@example.com"

    def test_get_accounts(self):
        """Test getting all accounts"""
        # Add test accounts first
        self.account_manager.add_account("acc1", "acc1@example.com")
        self.account_manager.add_account("acc2", "acc2@example.com")

        command = {
            "id": "test-2",
            "type": "GET_ACCOUNTS",
            "payload": {}
        }

        response = self.router.process_command(command)

        assert response["success"] == True
        assert len(response["data"]) == 2
        assert response["type"] == "GET_ACCOUNTS_RESPONSE"

        account_names = [acc["name"] for acc in response["data"]]
        assert "acc1" in account_names
        assert "acc2" in account_names

    def test_queue_creation(self):
        """Test queue creation with prompts"""
        prompts_data = [
            {
                "title": "Test Song 1",
                "lyrics": "Test lyrics 1",
                "style": "Pop"
            },
            {
                "title": "Test Song 2",
                "lyrics": "Test lyrics 2",
                "style": "Rock"
            }
        ]

        command = {
            "id": "test-3",
            "type": "CREATE_QUEUE",
            "payload": {
                "account_name": "test_account",
                "total_songs": 2,
                "songs_per_batch": 1,
                "prompts": prompts_data
            }
        }

        response = self.router.process_command(command)

        assert response["success"] == True
        assert response["type"] == "CREATE_QUEUE_RESPONSE"
        assert response["data"]["account_name"] == "test_account"
        assert response["data"]["total_songs"] == 2
        assert response["data"]["songs_per_batch"] == 1

    def test_validate_prompts(self):
        """Test prompt validation"""
        # First upload prompts to queue manager
        from src.utils.prompt_parser import SunoPrompt
        prompts = [
            SunoPrompt(title="Test 1", lyrics="Lyrics 1", style="Pop"),
            SunoPrompt(title="Test 2", lyrics="Lyrics 2", style="Rock")
        ]

        # Mock the queue manager to have prompts
        self.queue_manager.prompts = prompts
        self.queue_manager.prompt_cursor = 0

        command = {
            "id": "test-4",
            "type": "VALIDATE_PROMPTS",
            "payload": {
                "requested_total": 2
            }
        }

        response = self.router.process_command(command)

        assert response["success"] == True
        assert response["type"] == "VALIDATE_PROMPTS_RESPONSE"
        assert response["data"]["is_valid"] == True
        assert response["data"]["requested_total"] == 2
        assert response["data"]["available_slots"] == 2

    def test_error_handling_invalid_command(self):
        """Test error handling for invalid commands"""
        command = {
            "id": "test-5",
            "type": "UNKNOWN_COMMAND",
            "payload": {}
        }

        response = self.router.process_command(command)

        assert response["success"] == False
        assert "Unknown command type" in response["error"]
        assert response["error_code"] == "UNKNOWN_COMMAND"

    def test_error_handling_missing_payload(self):
        """Test error handling for missing required payload fields"""
        command = {
            "id": "test-6",
            "type": "CREATE_ACCOUNT",
            "payload": {}  # Missing 'name' field
        }

        response = self.router.process_command(command)

        assert response["success"] == False
        assert "Account name is required" in response["error"]
        assert response["error_code"] == "INVALID_PAYLOAD"

    def test_progress_manager_operation_tracking(self):
        """Test progress manager operation tracking"""
        progress_manager = ProgressManager()

        # Register operation
        operation_id = "test-operation-1"
        event = progress_manager.register_operation(operation_id)

        assert operation_id in progress_manager.active_operations
        assert not event.is_set()

        # Complete operation
        progress_manager.complete_operation(operation_id)

        assert operation_id not in progress_manager.active_operations
        assert event.is_set()

    def test_progress_callback_creation(self):
        """Test progress callback creation and execution"""
        progress_manager = ProgressManager()
        mock_message_handler = Mock()

        operation_id = "test-operation-2"
        callback = progress_manager.create_progress_callback(operation_id, mock_message_handler)

        # Execute callback
        callback("Test message", 50, "song-123", "processing", "Test Song")

        # Verify message handler was called
        mock_message_handler.send_progress_event.assert_called_once()

        # Check the payload
        call_args = mock_message_handler.send_progress_event.call_args
        payload = call_args[0][0]  # First positional argument

        assert payload["operation_id"] == operation_id
        assert payload["message"] == "Test message"
        assert payload["progress"] == 50
        assert payload["song_id"] == "song-123"
        assert payload["status"] == "processing"
        assert payload["title"] == "Test Song"


class TestStdinStdoutCommunication:
    """Test actual stdin/stdout communication with backend process"""

    def test_backend_process_startup(self):
        """Test backend process startup and ready message"""
        # Start backend process
        process = subprocess.Popen(
            ['python', 'backend/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )

        try:
            # Read ready message from stderr
            ready_line = process.stderr.readline()
            ready_data = json.loads(ready_line.strip())

            assert ready_data["type"] == "BACKEND_READY"
            assert "timestamp" in ready_data
            assert "version" in ready_data

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_account_creation_via_stdin(self):
        """Test account creation via stdin/stdout communication"""
        process = subprocess.Popen(
            ['python', 'backend/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )

        try:
            # Wait for ready message
            ready_line = process.stderr.readline()
            ready_data = json.loads(ready_line.strip())
            assert ready_data["type"] == "BACKEND_READY"

            # Send create account command
            command = {
                "id": "stdin-test-1",
                "type": "CREATE_ACCOUNT",
                "payload": {
                    "name": "stdin_test_account",
                    "email": "stdin_test@example.com"
                }
            }

            process.stdin.write(json.dumps(command) + '\n')
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            response = json.loads(response_line.strip())

            assert response["success"] == True
            assert response["data"]["name"] == "stdin_test_account"
            assert response["type"] == "CREATE_ACCOUNT_RESPONSE"

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_concurrent_commands(self):
        """Test handling concurrent commands"""
        process = subprocess.Popen(
            ['python', 'backend/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )

        try:
            # Wait for ready message
            ready_line = process.stderr.readline()
            json.loads(ready_line.strip())

            # Send multiple commands concurrently
            commands = [
                {
                    "id": "concurrent-1",
                    "type": "CREATE_ACCOUNT",
                    "payload": {"name": "concurrent_acc1", "email": "concurrent1@test.com"}
                },
                {
                    "id": "concurrent-2",
                    "type": "CREATE_ACCOUNT",
                    "payload": {"name": "concurrent_acc2", "email": "concurrent2@test.com"}
                },
                {
                    "id": "concurrent-3",
                    "type": "GET_ACCOUNTS",
                    "payload": {}
                }
            ]

            # Send all commands
            for command in commands:
                process.stdin.write(json.dumps(command) + '\n')
                process.stdin.flush()

            # Read all responses
            responses = []
            for _ in range(len(commands)):
                response_line = process.stdout.readline()
                response = json.loads(response_line.strip())
                responses.append(response)

            # Verify all commands were processed
            assert len(responses) == 3

            # Check account creation responses
            create_responses = [r for r in responses if r["type"] == "CREATE_ACCOUNT_RESPONSE"]
            assert len(create_responses) == 2

            # Check get accounts response
            get_accounts_response = next(r for r in responses if r["type"] == "GET_ACCOUNTS_RESPONSE")
            assert len(get_accounts_response["data"]) == 2

        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_error_recovery(self):
        """Test error recovery after invalid command"""
        process = subprocess.Popen(
            ['python', 'backend/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )

        try:
            # Wait for ready message
            ready_line = process.stderr.readline()
            json.loads(ready_line.strip())

            # Send invalid command
            invalid_command = {
                "id": "error-test-1",
                "type": "INVALID_COMMAND",
                "payload": {}
            }

            process.stdin.write(json.dumps(invalid_command) + '\n')
            process.stdin.flush()

            # Read error response
            error_response = json.loads(process.stdout.readline().strip())
            assert error_response["success"] == False

            # Send valid command after error
            valid_command = {
                "id": "error-test-2",
                "type": "CREATE_ACCOUNT",
                "payload": {"name": "recovery_account", "email": "recovery@test.com"}
            }

            process.stdin.write(json.dumps(valid_command) + '\n')
            process.stdin.flush()

            # Should get successful response
            success_response = json.loads(process.stdout.readline().strip())
            assert success_response["success"] == True
            assert success_response["data"]["name"] == "recovery_account"

        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    import sys

    # Run tests
    test_suite = TestCommunicationLayer()
    test_suite.setup_method()

    print("Running communication layer tests...")

    try:
        test_suite.test_account_creation()
        print("✅ Account creation test passed")

        test_suite.test_get_accounts()
        print("✅ Get accounts test passed")

        test_suite.test_queue_creation()
        print("✅ Queue creation test passed")

        test_suite.test_validate_prompts()
        print("✅ Prompt validation test passed")

        test_suite.test_error_handling_invalid_command()
        print("✅ Error handling test passed")

        test_suite.test_error_handling_missing_payload()
        print("✅ Missing payload test passed")

        test_suite.test_progress_manager_operation_tracking()
        print("✅ Progress manager test passed")

        test_suite.test_progress_callback_creation()
        print("✅ Progress callback test passed")

    finally:
        test_suite.teardown_method()

    print("\n🎉 All communication layer tests passed!")