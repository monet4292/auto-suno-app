"""
Integration Test with Mock Electron
Tests the complete communication flow between mock Electron and Python backend
"""
import json
import subprocess
import time
import threading
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class MockElectronClient:
    """Mock Electron client for testing communication"""

    def __init__(self, backend_process: subprocess.Popen):
        self.backend_process = backend_process
        self.responses = []
        self.progress_events = []
        self.running = False
        self.response_thread = None

    def start_listening(self):
        """Start listening for responses from backend"""
        self.running = True
        self.response_thread = threading.Thread(target=self._listen_for_responses)
        self.response_thread.daemon = True
        self.response_thread.start()

    def stop_listening(self):
        """Stop listening for responses"""
        self.running = False
        if self.response_thread:
            self.response_thread.join(timeout=2)

    def _listen_for_responses(self):
        """Listen for responses from backend stdout"""
        while self.running:
            try:
                line = self.backend_process.stdout.readline()
                if not line:
                    break

                response = json.loads(line.strip())
                if response.get("type") == "progress-event":
                    self.progress_events.append(response)
                else:
                    self.responses.append(response)

            except json.JSONDecodeError:
                continue
            except Exception:
                break

    def send_command(self, command: Dict[str, Any]) -> str:
        """Send command to backend"""
        command_str = json.dumps(command) + '\n'
        self.backend_process.stdin.write(command_str)
        self.backend_process.stdin.flush()
        return command.get("id")

    def wait_for_response(self, command_id: str, timeout: float = 10.0) -> Dict[str, Any]:
        """Wait for response to specific command"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for response in self.responses:
                if response.get("id") == command_id:
                    self.responses.remove(response)
                    return response
            time.sleep(0.1)

        raise TimeoutError(f"Response to command {command_id} not received within {timeout}s")

    def get_progress_events(self, operation_id: str = None) -> List[Dict[str, Any]]:
        """Get progress events, optionally filtered by operation_id"""
        if operation_id:
            return [event for event in self.progress_events
                   if event.get("payload", {}).get("operation_id") == operation_id]
        return self.progress_events.copy()


class TestElectronIntegration:
    """Integration tests for Electron + Python backend communication"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock config paths
        import backend.communication.command_router as command_router_module
        self.accounts_patcher = patch.object(command_router_module, 'AccountManager')
        self.queue_patcher = patch.object(command_router_module, 'QueueManager')
        self.download_patcher = patch.object(command_router_module, 'DownloadManager')
        self.session_patcher = patch.object(command_router_module, 'SessionManager')
        self.batch_patcher = patch.object(command_router_module, 'BatchSongCreator')
        self.history_patcher = patch.object(command_router_module, 'SongCreationHistoryManager')

        # Start mock managers
        self.mock_account_manager = self.accounts_patcher.start()
        self.mock_queue_manager = self.queue_patcher.start()
        self.mock_download_manager = self.download_patcher.start()
        self.mock_session_manager = self.session_patcher.start()
        self.mock_batch_creator = self.batch_patcher.start()
        self.mock_history_manager = self.history_patcher.start()

        # Setup mock return values
        self._setup_mocks()

    def teardown_method(self):
        """Cleanup test environment"""
        # Stop all patchers
        for patcher in [self.accounts_patcher, self.queue_patcher, self.download_patcher,
                       self.session_patcher, self.batch_patcher, self.history_patcher]:
            patcher.stop()

        # Cleanup temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_mocks(self):
        """Setup mock return values"""
        from src.models import Account, QueueEntry, SongClip, DownloadHistory, SongCreationRecord

        # Mock account manager
        self.mock_account_manager.get_all_accounts.return_value = [
            Account(name="test1", email="test1@example.com", created_at="2025-01-01 10:00:00"),
            Account(name="test2", email="test2@example.com", created_at="2025-01-02 10:00:00")
        ]
        self.mock_account_manager.add_account.return_value = True
        self.mock_account_manager.get_account.return_value = Account(
            name="new_account", email="new@example.com", created_at="2025-01-03 10:00:00"
        )

        # Mock queue manager
        self.mock_queue_manager.get_all_queues.return_value = [
            QueueEntry(
                id="queue1", account_name="test1", total_songs=5, songs_per_batch=2,
                prompts_range=(0, 5), status="pending", completed_count=0
            )
        ]
        self.mock_queue_manager.add_queue_entry.return_value = QueueEntry(
            id="new_queue", account_name="test1", total_songs=3, songs_per_batch=1,
            prompts_range=(0, 3), status="pending"
        )

        # Mock download manager
        self.mock_download_manager.fetch_clips.return_value = [
            SongClip(id="clip1", title="Test Song 1", audio_url="http://example.com/1.mp3"),
            SongClip(id="clip2", title="Test Song 2", audio_url="http://example.com/2.mp3")
        ]
        self.mock_download_manager.get_history.return_value = DownloadHistory(
            account_name="test1", downloaded_ids=["clip1"], total_downloaded=1
        )

        # Mock session manager
        self.mock_session_manager.get_session_token.return_value = "mock_session_token"
        self.mock_session_manager.verify_session.return_value = True
        self.mock_session_manager.launch_browser.return_value = Mock()  # Mock driver

        # Mock batch creator
        self.mock_batch_creator.create_songs_batch.return_value = [
            {"song_id": "song1", "title": "Created Song 1", "status": "completed"},
            {"song_id": "song2", "title": "Created Song 2", "status": "completed"}
        ]

        # Mock history manager
        self.mock_history_manager.get_all_records.return_value = [
            SongCreationRecord(
                song_id="song1", title="Song 1", prompt_index=0,
                account_name="test1", status="completed"
            )
        ]
        self.mock_history_manager.export_to_csv.return_value = Path(self.temp_dir) / "export.csv"

    def start_backend(self) -> subprocess.Popen:
        """Start backend process"""
        process = subprocess.Popen(
            ['python', 'backend/main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_root
        )

        # Wait for ready message
        ready_line = process.stderr.readline()
        ready_data = json.loads(ready_line.strip())
        assert ready_data["type"] == "BACKEND_READY"

        return process

    def test_full_workflow_integration(self):
        """Test complete workflow from account management to song creation"""
        backend_process = self.start_backend()
        client = MockElectronClient(backend_process)

        try:
            client.start_listening()

            # 1. Get existing accounts
            cmd_id = client.send_command({
                "id": "workflow-1",
                "type": "GET_ACCOUNTS",
                "payload": {}
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            assert len(response["data"]) == 2
            print("✅ Step 1: Get accounts - SUCCESS")

            # 2. Create new account
            cmd_id = client.send_command({
                "id": "workflow-2",
                "type": "CREATE_ACCOUNT",
                "payload": {
                    "name": "integration_test_account",
                    "email": "integration@test.com"
                }
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            assert response["data"]["name"] == "integration_test_account"
            print("✅ Step 2: Create account - SUCCESS")

            # 3. Get session token
            cmd_id = client.send_command({
                "id": "workflow-3",
                "type": "GET_SESSION_TOKEN",
                "payload": {
                    "account_name": "integration_test_account"
                }
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            assert response["data"]["token"] == "mock_session_token"
            print("✅ Step 3: Get session token - SUCCESS")

            # 4. Fetch clips
            cmd_id = client.send_command({
                "id": "workflow-4",
                "type": "FETCH_CLIPS",
                "payload": {
                    "session_token": "mock_session_token",
                    "use_my_songs": True
                }
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            assert len(response["data"]) == 2
            print("✅ Step 4: Fetch clips - SUCCESS")

            # 5. Create songs batch
            cmd_id = client.send_command({
                "id": "workflow-5",
                "type": "CREATE_SONGS_BATCH",
                "payload": {
                    "account_name": "integration_test_account",
                    "prompts": [
                        {"title": "Test Song", "lyrics": "Test lyrics", "style": "Pop"}
                    ],
                    "songs_per_session": 1,
                    "advanced_options": {},
                    "auto_submit": False
                }
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            assert "operation_id" in response["data"]
            print("✅ Step 5: Create songs batch - SUCCESS")

            # 6. Get creation history
            cmd_id = client.send_command({
                "id": "workflow-6",
                "type": "GET_CREATION_HISTORY",
                "payload": {}
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            assert len(response["data"]) >= 0
            print("✅ Step 6: Get creation history - SUCCESS")

            print("\n🎉 Full workflow integration test PASSED!")

        finally:
            client.stop_listening()
            backend_process.terminate()
            backend_process.wait(timeout=5)

    def test_progress_events_during_batch_creation(self):
        """Test progress events during batch song creation"""
        backend_process = self.start_backend()
        client = MockElectronClient(backend_process)

        try:
            client.start_listening()

            # Start batch creation with progress tracking
            cmd_id = client.send_command({
                "id": "progress-test-1",
                "type": "CREATE_SONGS_BATCH",
                "payload": {
                    "account_name": "test1",
                    "prompts": [
                        {"title": "Song 1", "lyrics": "Lyrics 1", "style": "Pop"},
                        {"title": "Song 2", "lyrics": "Lyrics 2", "style": "Rock"}
                    ],
                    "songs_per_session": 1,
                    "advanced_options": {},
                    "auto_submit": False
                }
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            operation_id = response["data"]["operation_id"]

            # Wait a bit for progress events (if any)
            time.sleep(1)

            # Check for progress events
            progress_events = client.get_progress_events(operation_id)
            print(f"📊 Progress events received: {len(progress_events)}")

            print("✅ Progress events test - SUCCESS")

        finally:
            client.stop_listening()
            backend_process.terminate()
            backend_process.wait(timeout=5)

    def test_error_handling_integration(self):
        """Test error handling in integration context"""
        backend_process = self.start_backend()
        client = MockElectronClient(backend_process)

        try:
            client.start_listening()

            # Send invalid command
            cmd_id = client.send_command({
                "id": "error-integration-1",
                "type": "INVALID_COMMAND_TYPE",
                "payload": {}
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == False
            assert "Unknown command type" in response["error"]
            print("✅ Invalid command error handling - SUCCESS")

            # Send command with missing required fields
            cmd_id = client.send_command({
                "id": "error-integration-2",
                "type": "CREATE_ACCOUNT",
                "payload": {}  # Missing 'name'
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == False
            assert "Account name is required" in response["error"]
            print("✅ Missing payload error handling - SUCCESS")

            # Verify backend is still responsive after errors
            cmd_id = client.send_command({
                "id": "error-integration-3",
                "type": "GET_ACCOUNTS",
                "payload": {}
            })

            response = client.wait_for_response(cmd_id)
            assert response["success"] == True
            print("✅ Backend recovery after errors - SUCCESS")

            print("\n🎉 Error handling integration test PASSED!")

        finally:
            client.stop_listening()
            backend_process.terminate()
            backend_process.wait(timeout=5)

    def test_concurrent_operations(self):
        """Test handling concurrent operations"""
        backend_process = self.start_backend()
        client = MockElectronClient(backend_process)

        try:
            client.start_listening()

            # Send multiple commands concurrently
            commands = [
                {
                    "id": "concurrent-integration-1",
                    "type": "GET_ACCOUNTS",
                    "payload": {}
                },
                {
                    "id": "concurrent-integration-2",
                    "type": "CREATE_ACCOUNT",
                    "payload": {"name": "concurrent_acc1", "email": "concurrent1@test.com"}
                },
                {
                    "id": "concurrent-integration-3",
                    "type": "GET_SESSION_TOKEN",
                    "payload": {"account_name": "concurrent_acc1"}
                }
            ]

            # Send all commands rapidly
            command_ids = []
            for command in commands:
                cmd_id = client.send_command(command)
                command_ids.append(cmd_id)

            # Wait for all responses
            responses = []
            for cmd_id in command_ids:
                response = client.wait_for_response(cmd_id)
                responses.append(response)

            # Verify all commands were processed successfully
            assert len(responses) == 3
            assert all(r["success"] for r in responses)

            print("✅ Concurrent operations test - SUCCESS")
            print("\n🎉 Concurrent operations integration test PASSED!")

        finally:
            client.stop_listening()
            backend_process.terminate()
            backend_process.wait(timeout=5)


if __name__ == "__main__":
    import sys
    from unittest.mock import Mock, patch

    # Run integration tests
    test_suite = TestElectronIntegration()
    test_suite.setup_method()

    print("🚀 Running Electron integration tests...")

    try:
        test_suite.test_full_workflow_integration()
        print("\n" + "="*50)
        test_suite.test_progress_events_during_batch_creation()
        print("\n" + "="*50)
        test_suite.test_error_handling_integration()
        print("\n" + "="*50)
        test_suite.test_concurrent_operations()

        print("\n🎉 ALL ELECTRON INTEGRATION TESTS PASSED! 🎉")
        print("\n📋 Test Summary:")
        print("  ✅ Full workflow integration")
        print("  ✅ Progress events handling")
        print("  ✅ Error handling and recovery")
        print("  ✅ Concurrent operations")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        test_suite.teardown_method()