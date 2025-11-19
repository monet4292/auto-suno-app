# Task Completion Checklist
1. Ensure feature follows Clean Architecture layering and module-specific AGENTS.md guidance.
2. Update relevant docs: README, CLAUDE.md, CHANGELOG, docs/, memory-bank entries when behavior changes.
3. Run `python -m compileall src` (sanity) and `pytest`/`python -m pytest tests` as appropriate; capture results.
4. Confirm logging uses `logger` and no hard-coded paths/values leak outside `config.settings`.
5. Verify data/log/profile directories remain gitignored; no sensitive artifacts committed.
6. Summarize changes + tests in final response; propose next steps if additional validation (e.g., GUI smoke via `python app.py`) is pending.