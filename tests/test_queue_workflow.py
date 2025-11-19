"""
Integration-style tests for queue + history workflows.
"""
from pathlib import Path

import pytest

from src.core import QueueManager
from src.core.song_creation_history_manager import SongCreationHistoryManager
from src.models import SongCreationRecord
from tests.test_utils import make_prompts


def _complete_queue(queue_manager: QueueManager, history_manager: SongCreationHistoryManager, entry, status: str = "success"):
    for offset in range(entry.total_songs):
        history_manager.add_creation_record(SongCreationRecord(
            song_id=f"{entry.account_name}-{offset:02d}",
            title=f"{entry.account_name} track {offset + 1}",
            prompt_index=entry.prompts_range[0] + offset,
            account_name=entry.account_name,
            status=status,
        ))
    queue_manager.update_queue_progress(
        entry.id,
        completed_count=entry.total_songs,
        status="completed" if status == "success" else "failed",
    )


def test_full_workflow_e2e(tmp_path: Path):
    queue_path = tmp_path / "queue.json"
    history_path = tmp_path / "history.json"
    queue_manager = QueueManager(queue_path)
    history_manager = SongCreationHistoryManager(history_path)

    prompts = make_prompts(120)
    entry_one = queue_manager.add_queue_entry("acc1", 30, 5, prompts)
    entry_two = queue_manager.add_queue_entry("acc2", 25, 5, prompts)
    entry_three = queue_manager.add_queue_entry("acc3", 15, 5, prompts)

    _complete_queue(queue_manager, history_manager, entry_one)
    _complete_queue(queue_manager, history_manager, entry_two)
    _complete_queue(queue_manager, history_manager, entry_three, status="failed")

    assert len(history_manager.get_all_records()) == 70
    assert queue_manager.get_queue(entry_one.id).status == "completed"
    assert queue_manager.get_queue(entry_two.id).status == "completed"
    assert queue_manager.get_queue(entry_three.id).status == "failed"


def test_resume_from_state(tmp_path: Path):
    queue_path = tmp_path / "queue.json"
    queue_manager = QueueManager(queue_path)
    prompts = make_prompts(40)
    entry = queue_manager.add_queue_entry("resume-acc", 20, 10, prompts)
    queue_manager.update_queue_progress(entry.id, completed_count=10, status="in_progress")

    fresh_manager = QueueManager(queue_path)
    loaded_entry = fresh_manager.get_queue(entry.id)
    assert loaded_entry is not None
    assert loaded_entry.completed_count == 10
    assert loaded_entry.status == "in_progress"

    fresh_manager.update_queue_progress(entry.id, completed_count=20, status="completed")
    final_manager = QueueManager(queue_path)
    assert final_manager.get_queue(entry.id).status == "completed"


def test_three_accounts_history(tmp_path: Path):
    queue_path = tmp_path / "queue.json"
    history_path = tmp_path / "history.json"
    queue_manager = QueueManager(queue_path)
    history_manager = SongCreationHistoryManager(history_path)
    prompts = make_prompts(50)

    accounts = ["alpha", "beta", "gamma"]
    entries = [
        queue_manager.add_queue_entry(name, 10, 5, prompts)
        for name in accounts
    ]

    for entry in entries:
        _complete_queue(queue_manager, history_manager, entry)

    records = history_manager.get_all_records()
    assert len(records) == 30
    assert {rec.account_name for rec in records} == set(accounts)
