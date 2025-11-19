"""
Queue manager - orchestrates prompt queues per account.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from config.settings import QUEUE_STATE_FILE
from src.models import QueueEntry
from src.utils import atomic_write_json, load_json, logger
from src.utils.prompt_parser import SunoPrompt


class QueueValidationError(Exception):
    """Raised when queue state violates prompt limits or input rules."""


class QueueManager:
    """Manages queue entries and persistence for multi-account song creation."""

    def __init__(self, state_file: Path = QUEUE_STATE_FILE):
        self.state_file = state_file
        self.version = "1.0"
        self.prompts: List[SunoPrompt] = []
        self.prompt_cursor = 0
        self.queues: Dict[str, QueueEntry] = {}
        self.last_updated: Optional[str] = None
        self._load_state()

    def _load_state(self) -> None:
        """Load the queue state from disk."""
        data = load_json(self.state_file, self._default_state())
        self.version = data.get("version", "1.0")
        self.prompts = self._deserialize_prompts(data.get("prompts", []))
        self.prompt_cursor = data.get("prompt_cursor", 0)
        self.last_updated = data.get("last_updated")
        self.queues = {}
        for raw in data.get("queues", []):
            try:
                entry = QueueEntry.from_dict(raw)
                self.queues[entry.id] = entry
            except KeyError:
                logger.warning("Skipped malformed queue entry during load")
        logger.info(f"Queue state loaded ({len(self.queues)} entries)")

    def _default_state(self) -> dict[str, object]:
        return {
            "version": self.version,
            "prompts": [],
            "prompt_cursor": 0,
            "queues": [],
            "last_updated": None,
        }

    def _deserialize_prompts(self, data: List[dict[str, str]]) -> List[SunoPrompt]:
        prompts: List[SunoPrompt] = []
        for item in data:
            title = item.get("title", "")
            lyrics = item.get("lyrics", "")
            style = item.get("style", "")
            if title and lyrics and style:
                prompts.append(SunoPrompt(title=title, lyrics=lyrics, style=style))
        return prompts

    def _serialize_prompts(self) -> List[dict[str, str]]:
        return [
            {"title": prompt.title, "lyrics": prompt.lyrics, "style": prompt.style}
            for prompt in self.prompts
        ]

    def _ensure_prompts(self, prompts: List[SunoPrompt]) -> None:
        if not prompts:
            raise QueueValidationError("At least one prompt is required to queue songs")
        if self.prompts and self.prompts != prompts and self.queues:
            raise QueueValidationError("Cannot switch prompts while queues exist")
        if not self.prompts or self.prompts != prompts:
            self.prompts = list(prompts)
            self.prompt_cursor = 0

    def _save_state(self) -> bool:
        payload = {
            "version": self.version,
            "prompts": self._serialize_prompts(),
            "prompt_cursor": self.prompt_cursor,
            "queues": [entry.to_dict() for entry in self.queues.values()],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if atomic_write_json(self.state_file, payload):
            self.last_updated = payload["last_updated"]
            logger.info(f"Queue state saved ({len(self.queues)} entries)")
            return True
        logger.error("Failed to persist queue state")
        return False

    def add_queue_entry(
        self,
        account_name: str,
        total_songs: int,
        songs_per_batch: int,
        prompts: List[SunoPrompt],
    ) -> QueueEntry:
        """
        Add a new queue entry if prompts remain.

        Args:
            account_name: Account responsible for the queue.
            total_songs: Number of songs to create for this entry.
            songs_per_batch: Number of songs to create per browser session.
            prompts: List of parsed SunoPrompt objects.
        """
        self._ensure_prompts(prompts)
        if total_songs <= 0 or songs_per_batch <= 0:
            raise QueueValidationError("Song counts must be positive")
        if songs_per_batch > total_songs:
            raise QueueValidationError("Songs per batch cannot exceed total songs")
        if self.prompt_cursor + total_songs > len(self.prompts):
            raise QueueValidationError("Not enough prompts remain to fulfill request")
        entry = QueueEntry(
            id=str(uuid4()),
            account_name=account_name,
            total_songs=total_songs,
            songs_per_batch=songs_per_batch,
            prompts_range=(self.prompt_cursor, self.prompt_cursor + total_songs),
        )
        self.prompt_cursor += total_songs
        self.queues[entry.id] = entry
        self._save_state()
        return entry

    def remove_queue_entry(self, queue_id: str) -> bool:
        """Remove a queue entry by its ID."""
        if queue_id not in self.queues:
            return False
        del self.queues[queue_id]
        self._save_state()
        return True

    def get_queue(self, queue_id: str) -> Optional[QueueEntry]:
        """Return a queue entry by ID."""
        return self.queues.get(queue_id)

    def get_all_queues(self) -> List[QueueEntry]:
        """Return all queue entries in creation order."""
        return sorted(self.queues.values(), key=lambda entry: entry.created_at)

    def get_pending_queues(self) -> List[QueueEntry]:
        """Return queue entries that are not completed or failed yet."""
        return [
            entry
            for entry in self.queues.values()
            if entry.status in {"pending", "in_progress"}
        ]

    def update_queue_progress(
        self,
        queue_id: str,
        completed_count: Optional[int] = None,
        status: Optional[str] = None,
    ) -> bool:
        """Update progress metrics for a queue entry."""
        entry = self.queues.get(queue_id)
        if not entry:
            return False
        if completed_count is not None:
            entry.completed_count = min(completed_count, entry.total_songs)
        if status:
            entry.status = status
        self._save_state()
        return True

    def validate_total_prompts(self, requested_total: int) -> bool:
        """Verify that enough prompts remain before creating a queue."""
        return requested_total <= self.available_prompt_slots

    @property
    def available_prompt_slots(self) -> int:
        """Number of prompts still unassigned."""
        return len(self.prompts) - self.prompt_cursor

    def clear(self) -> None:
        """Reset queue state completely (prompts and entries)."""
        self.prompts = []
        self.prompt_cursor = 0
        self.queues.clear()
        self._save_state()
