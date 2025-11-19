"""
Utility helper functions for common operations
"""
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import logger


def load_json(filepath: Path, default: Optional[Any] = None) -> Any:
    """
    Load JSON file from disk.
    
    Args:
        filepath: Path to JSON file
        default: Default value if file doesn't exist or error occurs
        
    Returns:
        Parsed JSON data or default value
    """
    if not filepath.exists():
        return default if default is not None else {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default if default is not None else {}


def save_json(filepath: Path, data: Any) -> bool:
    """
    Save data to JSON file.
    
    Args:
        filepath: Path to JSON file
        data: Data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def atomic_write_json(filepath: Path, data: Any) -> bool:
    """
    Atomically write JSON to disk to avoid partial state files.
    """
    temp_file = None
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = filepath.parent
        with tempfile.NamedTemporaryFile(
            'w', encoding='utf-8', delete=False, dir=temp_dir
        ) as tmp:
            json.dump(data, tmp, indent=4, ensure_ascii=False)
            temp_file = Path(tmp.name)
        os.replace(temp_file, filepath)
        return True
    except Exception as exc:
        logger.error(f"Atomic write failed for {filepath}: {exc}")
        if temp_file and temp_file.exists():
            temp_file.unlink(missing_ok=True)
        return False


def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for Windows/Unix filesystems
    """
    # Remove invalid characters for Windows
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename or "untitled"


def format_filesize(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if not seconds:
        return "00:00"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_datetime(dt_str: str) -> str:
    """
    Format datetime string to readable format.
    
    Args:
        dt_str: Datetime string in format "YYYY-MM-DD HH:MM:SS"
        
    Returns:
        Formatted datetime string or "N/A" if invalid
    """
    if not dt_str:
        return "N/A"
    
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return dt_str


def validate_profile_name(name: str) -> bool:
    """
    Validate Suno profile name format.
    
    Args:
        name: Profile name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False
    
    # Must start with @
    if not name.startswith('@'):
        return False
    
    # Only alphanumeric and underscore after @
    username = name[1:]
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def get_file_extension(url: str, default: str = '.mp3') -> str:
    """
    Get file extension from URL.
    
    Args:
        url: URL string
        default: Default extension if unable to parse
        
    Returns:
        File extension with dot (e.g., ".mp3")
    """
    try:
        from urllib.parse import urlparse
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        return ext if ext else default
    except Exception:
        return default


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        The path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_unique_filename(filepath: Path) -> Path:
    """
    Get unique filename by appending number if file exists.
    
    Args:
        filepath: Original filepath
        
    Returns:
        Unique filepath
    """
    if not filepath.exists():
        return filepath
    
    counter = 1
    stem = filepath.stem
    suffix = filepath.suffix
    parent = filepath.parent
    
    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
