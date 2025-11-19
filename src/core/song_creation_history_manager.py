"""
Manage persistence of song creation history records.
"""
import csv
import json
from pathlib import Path
from typing import List

from config.settings import SONG_CREATION_HISTORY_FILE
from src.models import SongCreationRecord
from src.utils import logger


class SongCreationHistoryManager:
    """Persistent manager for SongCreationRecord entries."""

    def __init__(self, file_path: Path | None = None):
        self.file_path = file_path or SONG_CREATION_HISTORY_FILE
        self.records: List[SongCreationRecord] = []
        self._ensure_file()
        self.load_records()

    def _ensure_file(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def load_records(self):
        """Load records from disk."""
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            logger.error(f"Failed to load song creation history: {exc}")
            data = []

        self.records = [
            SongCreationRecord.from_dict(record) for record in data if isinstance(record, dict)
        ]

    def _save(self):
        try:
            with self.file_path.open("w", encoding="utf-8") as handle:
                json.dump([record.to_dict() for record in self.records], handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.error(f"Unable to save song creation history: {exc}")

    def add_creation_record(self, record: SongCreationRecord):
        """Store a new record and persist immediately."""
        self.records.insert(0, record)
        self._save()

    def get_all_records(self) -> List[SongCreationRecord]:
        """Return all records sorted newest first."""
        return list(self.records)

    def get_records_by_account(self, account_name: str) -> List[SongCreationRecord]:
        """Return records filtered by account."""
        return [rec for rec in self.records if rec.account_name == account_name]

    def search_records(self, keyword: str) -> List[SongCreationRecord]:
        """Search records by title, song ID, or status."""
        if not keyword:
            return self.get_all_records()

        lower = keyword.lower()
        return [
            rec for rec in self.records
            if lower in rec.title.lower()
            or lower in rec.song_id.lower()
            or lower in rec.status.lower()
        ]

    def export_to_csv(self, output_path: Path) -> Path:
        """Export the current records to CSV."""
        fields = ["timestamp", "account", "title", "song_id", "status", "error"]
        try:
            with output_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(fields)
                for rec in self.records:
                    writer.writerow([
                        rec.created_at,
                        rec.account_name,
                        rec.title,
                        rec.song_id,
                        rec.status,
                        rec.error_message or ""
                    ])
        except Exception as exc:
            logger.error(f"Failed to export song creation history to CSV: {exc}")
            raise
        return output_path
