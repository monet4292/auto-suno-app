"""
Core package
"""
from importlib import import_module

__all__ = [
    'AccountManager',
    'SessionManager',
    'DownloadManager',
    'QueueManager',
    'SongCreationHistoryManager'
]


def __getattr__(name: str):
    if name in __all__:
        module_name = "".join(
            f"_{ch.lower()}" if ch.isupper() else ch
            for ch in name
        ).lstrip("_")
        module = import_module(f".{module_name}", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
