"""
Data Models
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, List, Optional, Tuple
import json


@dataclass
class Account:
    """Account model"""
    name: str
    email: str
    created_at: str
    last_used: Optional[str] = None
    status: str = "active"
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class DownloadHistory:
    """Download history for an account"""
    account_name: str
    downloaded_ids: List[str] = field(default_factory=list)
    total_downloaded: int = 0
    last_download: Optional[str] = None
    current_page: int = 1
    last_profile: str = ""
    
    def add_download(self, clip_id: str):
        """Add a downloaded clip ID"""
        if clip_id not in self.downloaded_ids:
            self.downloaded_ids.append(clip_id)
            self.total_downloaded = len(self.downloaded_ids)
            self.last_download = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def is_downloaded(self, clip_id: str) -> bool:
        """Check if clip was already downloaded"""
        return clip_id in self.downloaded_ids
    
    def clear(self):
        """Clear download history"""
        self.downloaded_ids = []
        self.total_downloaded = 0
        self.last_download = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class SongClip:
    """Song clip model"""
    id: str
    title: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: str = ""
    created_at: Optional[str] = None
    duration: Optional[float] = None
    
    @classmethod
    def from_api_response(cls, data: dict):
        """Create from API response"""
        return cls(
            id=data.get('id', ''),
            title=data.get('title', 'Unknown'),
            audio_url=data.get('audio_url'),
            image_url=data.get('image_url') or data.get('image_large_url'),
            tags=data.get('metadata', {}).get('tags', ''),
            created_at=data.get('created_at'),
            duration=data.get('metadata', {}).get('duration_formatted')
        )


@dataclass
class DownloadTask:
    """Download task model"""
    clip: SongClip
    output_dir: str
    with_thumbnail: bool = True
    append_uuid: bool = True
    status: str = "pending"  # pending, downloading, completed, failed
    progress: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self):
        result = asdict(self)
        result['clip'] = asdict(self.clip)
        return result


@dataclass
class QueueEntry:
    """Queue entry describing a portion of the prompt upload."""
    id: str
    account_name: str
    total_songs: int
    songs_per_batch: int
    prompts_range: Tuple[int, int]
    status: str = "pending"
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    completed_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data['prompts_range'] = list(self.prompts_range)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueueEntry":
        prompts_range = tuple(data.get("prompts_range", (0, 0)))
        return cls(
            id=data["id"],
            account_name=data["account_name"],
            total_songs=data.get("total_songs", 0),
            songs_per_batch=data.get("songs_per_batch", 1),
            prompts_range=prompts_range,
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            completed_count=data.get("completed_count", 0)
        )


@dataclass
class SongCreationRecord:
    """Record of a generated song for history panel tracking."""
    song_id: str
    title: str
    prompt_index: int
    account_name: str
    status: str
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    error_message: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SongCreationRecord":
        return cls(
            song_id=data["song_id"],
            title=data["title"],
            prompt_index=data["prompt_index"],
            account_name=data["account_name"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            error_message=data.get("error_message")
        )
