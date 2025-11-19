"""
Stress tests that hit QueueManager persistence and status toggles.
"""
from pathlib import Path

from src.core import QueueManager
from tests.test_utils import make_prompts


def test_queue_survives_100_song_batch(tmp_path: Path):
    manager = QueueManager(tmp_path / "stress-queue.json")
    prompts = make_prompts(200)
    entry = manager.add_queue_entry("stress-user", 100, 10, prompts)

    for completed in range(entry.total_songs + 1):
        manager.update_queue_progress(entry.id, completed_count=completed, status="in_progress")

    final = manager.get_queue(entry.id)
    assert final.completed_count == 100
    assert final.status == "in_progress"
    assert manager.available_prompt_slots == 100


def test_start_stop_rapid_toggle(tmp_path: Path):
    manager = QueueManager(tmp_path / "rapid.json")
    prompts = make_prompts(60)
    entry = manager.add_queue_entry("toggle-user", 30, 5, prompts)

    for iteration in range(30):
        status = "pending" if iteration % 2 else "in_progress"
        manager.update_queue_progress(entry.id, completed_count=iteration, status=status)

    reloaded = QueueManager(tmp_path / "rapid.json").get_queue(entry.id)
    assert reloaded.status in {"pending", "in_progress"}
