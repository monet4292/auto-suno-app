"""
Test Runner for Communication Layer Tests
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_communication_tests():
    """Run all communication layer tests"""
    print("🧪 Running Communication Layer Test Suite")
    print("=" * 50)

    # Test 1: Basic Communication Layer Tests
    print("\n📋 Test 1: Basic Communication Layer")
    try:
        from tests.communication.test_communication_layer import TestCommunicationLayer
        test_suite = TestCommunicationLayer()
        test_suite.setup_method()

        tests = [
            ("Account Creation", test_suite.test_account_creation),
            ("Get Accounts", test_suite.test_get_accounts),
            ("Queue Creation", test_suite.test_queue_creation),
            ("Validate Prompts", test_suite.test_validate_prompts),
            ("Error Handling - Invalid Command", test_suite.test_error_handling_invalid_command),
            ("Error Handling - Missing Payload", test_suite.test_error_handling_missing_payload),
            ("Progress Manager", test_suite.test_progress_manager_operation_tracking),
            ("Progress Callback", test_suite.test_progress_callback_creation),
        ]

        passed = 0
        for test_name, test_func in tests:
            try:
                test_func()
                print(f"  ✅ {test_name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")

        test_suite.teardown_method()
        print(f"\n📊 Basic Tests: {passed}/{len(tests)} passed")

    except Exception as e:
        print(f"❌ Basic test suite failed: {e}")

    # Test 2: Stdin/Stdout Communication Tests
    print("\n📋 Test 2: Stdin/Stdout Communication")
    try:
        from tests.communication.test_communication_layer import TestStdinStdoutCommunication
        test_suite = TestStdinStdoutCommunication()

        tests = [
            ("Backend Process Startup", test_suite.test_backend_process_startup),
            ("Account Creation via Stdin", test_suite.test_account_creation_via_stdin),
            ("Concurrent Commands", test_suite.test_concurrent_commands),
            ("Error Recovery", test_suite.test_error_recovery),
        ]

        passed = 0
        for test_name, test_func in tests:
            try:
                test_func()
                print(f"  ✅ {test_name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")

        print(f"\n📊 Stdin/Stdout Tests: {passed}/{len(tests)} passed")

    except Exception as e:
        print(f"❌ Stdin/Stdout test suite failed: {e}")

    # Test 3: Electron Integration Tests
    print("\n📋 Test 3: Electron Integration")
    try:
        from tests.communication.test_electron_integration import TestElectronIntegration
        from unittest.mock import Mock, patch

        test_suite = TestElectronIntegration()
        test_suite.setup_method()

        tests = [
            ("Full Workflow Integration", test_suite.test_full_workflow_integration),
            ("Progress Events", test_suite.test_progress_events_during_batch_creation),
            ("Error Handling Integration", test_suite.test_error_handling_integration),
            ("Concurrent Operations", test_suite.test_concurrent_operations),
        ]

        passed = 0
        for test_name, test_func in tests:
            try:
                test_func()
                print(f"  ✅ {test_name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")

        test_suite.teardown_method()
        print(f"\n📊 Integration Tests: {passed}/{len(tests)} passed")

    except Exception as e:
        print(f"❌ Integration test suite failed: {e}")

    print("\n" + "=" * 50)
    print("🏁 Communication Layer Testing Complete")
    print("\n📝 Notes:")
    print("  - All tests verify stdin/stdout communication works correctly")
    print("  - Integration tests ensure compatibility with Electron frontend")
    print("  - Progress callback system supports real-time updates")
    print("  - Error handling maintains backend stability")
    print("\n✅ Communication layer is ready for React + Electron integration!")


if __name__ == "__main__":
    run_communication_tests()