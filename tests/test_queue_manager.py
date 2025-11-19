"""
Tests for the QueueManager core behaviors.
"""
import json
from pathlib import Path

import pytest

from src.core.queue_manager import QueueManager, QueueValidationError
from src.utils.prompt_parser import SunoPrompt


@pytest.fixture
def sample_prompts() -> list[SunoPrompt]:
    """Return a small set of parsed prompts."""
    return [
        SunoPrompt(
            title=f"Song {i}",
            lyrics="Sample lyrics content",
            style="Pop"
        )
        for i in range(1, 6)
    ]


def test_add_queue_entry_records_state(tmp_path: Path, sample_prompts: list[SunoPrompt]):
    state_file = tmp_path / "queue_state.json"
    manager = QueueManager(state_file=state_file)

    entry = manager.add_queue_entry(
        account_name="acc1",
        total_songs=2,
        songs_per_batch=1,
        prompts=sample_prompts
    )

    assert entry.account_name == "acc1"
    assert entry.total_songs == 2
    assert manager.available_prompt_slots == len(sample_prompts) - 2
    assert state_file.exists()

    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert len(data["queues"]) == 1
    assert data["queues"][0]["account_name"] == "acc1"


def test_add_queue_entry_validation(tmp_path: Path, sample_prompts: list[SunoPrompt]):
    manager = QueueManager(state_file=tmp_path / "queue_state.json")

    with pytest.raises(QueueValidationError):
        manager.add_queue_entry(
            account_name="acc1",
            total_songs=0,
            songs_per_batch=1,
            prompts=sample_prompts
        )

    with pytest.raises(QueueValidationError):
        manager.add_queue_entry(
            account_name="acc1",
            total_songs=5,
            songs_per_batch=6,
            prompts=sample_prompts
        )

    manager.add_queue_entry(
        account_name="acc1",
        total_songs=5,
        songs_per_batch=5,
        prompts=sample_prompts
    )

    with pytest.raises(QueueValidationError):
        manager.add_queue_entry(
            account_name="acc2",
            total_songs=1,
            songs_per_batch=1,
            prompts=sample_prompts
        )


def test_remove_queue_entry_updates_state(tmp_path: Path, sample_prompts: list[SunoPrompt]):
    state_file = tmp_path / "queue_state.json"
    manager = QueueManager(state_file=state_file)

    entry = manager.add_queue_entry(
        account_name="acc1",
        total_songs=3,
        songs_per_batch=3,
        prompts=sample_prompts
    )

    assert manager.remove_queue_entry(entry.id)
    assert manager.get_queue(entry.id) is None
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert not data["queues"]


def test_persistence_reloads_entries(tmp_path: Path, sample_prompts: list[SunoPrompt]):
    state_file = tmp_path / "queue_state.json"
    manager = QueueManager(state_file=state_file)
    manager.add_queue_entry(
        account_name="acc1",
        total_songs=2,
        songs_per_batch=2,
        prompts=sample_prompts
    )

    reloaded = QueueManager(state_file=state_file)
    entries = reloaded.get_all_queues()
    assert len(entries) == 1
    assert entries[0].account_name == "acc1"
    assert reloaded.prompts == manager.prompts


def test_update_queue_progress_persists(tmp_path: Path, sample_prompts: list[SunoPrompt]):
    state_file = tmp_path / "queue_state.json"
    manager = QueueManager(state_file=state_file)
    entry = manager.add_queue_entry(
        account_name="acc1",
        total_songs=2,
        songs_per_batch=1,
        prompts=sample_prompts
    )

    assert manager.update_queue_progress(entry.id, completed_count=2, status="completed")
    reloaded = QueueManager(state_file=state_file)
    updated_entry = reloaded.get_queue(entry.id)
    assert updated_entry is not None
    assert updated_entry.completed_count == 2
    assert updated_entry.status == "completed"
