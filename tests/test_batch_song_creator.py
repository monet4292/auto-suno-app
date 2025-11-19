"""
Unit tests for BatchSongCreator batch/session logic.
"""
from types import SimpleNamespace
from pathlib import Path

import pytest

from src.core.batch_song_creator import BatchSongCreator
from src.utils.prompt_parser import SunoPrompt


@pytest.fixture
def sample_prompts() -> list[SunoPrompt]:
    """Return a list of mock prompts for testing."""
    return [
        SunoPrompt(title=f"Song {i}", lyrics="Lyrics", style="Pop")
        for i in range(1, 8)
    ]


def test_create_songs_batch_splits_sessions(monkeypatch, sample_prompts):
    """Verify create_songs_batch splits prompts into sessions of given size."""
    creator = BatchSongCreator(Path("dummy"))
    session_calls = []

    def fake_run_session(
        self,
        prompts,
        advanced_options,
        auto_submit,
        progress_callback,
        session_index,
        session_count,
        completed_before_session,
        total_songs,
        account_name=None,
        history_manager=None
    ):
        session_calls.append((session_index, len(prompts), completed_before_session))
        return [{'title': p.title, 'success': True, 'error': None} for p in prompts]

    monkeypatch.setattr(BatchSongCreator, "_run_session", fake_run_session)
    monkeypatch.setattr(BatchSongCreator, "_initialize_driver", lambda self: None)
    monkeypatch.setattr(BatchSongCreator, "_teardown_driver", lambda self: None)

    callback = []

    def progress_cb(message, progress, song_id, status, prompt_title):
        callback.append((message, progress, song_id, status, prompt_title))

    creator.create_songs_batch(
        sample_prompts,
        songs_per_session=3,
        advanced_options={},
        auto_submit=False,
        progress_callback=progress_cb
    )

    assert len(session_calls) == 3
    for idx, (_, session_length, _) in enumerate(session_calls):
        expected = 3 if idx < 2 else len(sample_prompts) % 3 or 3
        assert session_length == expected
    assert callback[-1][0] == "✅ Hoàn thành!"


def test_run_session_emits_song_ids(monkeypatch):
    """Ensure _run_session invokes progress callback with song_id on auto-submit."""
    prompts = [SunoPrompt(title=f"Track {i}", lyrics="X", style="Pop") for i in range(3)]
    creator = BatchSongCreator(Path("dummy"))

    driver = SimpleNamespace(
        window_handles=[f"tab{i}" for i in range(3)],
        switch_to=SimpleNamespace(window=None),
        get=lambda url: None,
        execute_script=lambda script: None,
        quit=lambda: None
    )

    creator.driver = driver
    monkeypatch.setattr(BatchSongCreator, "_fill_song_form", lambda self, prompt, tab_handle, adv, idx: True)
    song_ids = iter([f"id-{i}" for i in range(3)])
    monkeypatch.setattr(BatchSongCreator, "_submit_and_get_id", lambda self, tab_handle: next(song_ids))

    records = []

    def progress_cb(message, progress, song_id, status, prompt_title):
        records.append((message, progress, song_id, status, prompt_title))

    results = creator._run_session(
        prompts=prompts,
        advanced_options={},
        auto_submit=True,
        progress_callback=progress_cb,
        session_index=0,
        session_count=1,
        completed_before_session=0,
        total_songs=len(prompts)
    )

    assert len(results) == 3
    assert all(entry['success'] for entry in results)
    assert all(record[2] is not None for record in records)
