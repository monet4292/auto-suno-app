"""
UI Package
"""
from __future__ import annotations

__all__ = ['MainWindow', 'run_app']


def __getattr__(name: str):
    if name == "MainWindow":
        from .main_window import MainWindow
        return MainWindow
    if name == "run_app":
        from .main_window import run_app
        return run_app
    raise AttributeError(f"module {__name__} has no attribute {name}")
