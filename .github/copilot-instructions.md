## Copilot agent quick guide — Auto-Suno-App (concise)

This file lists repository-specific rules and shortcuts an AI coding agent should follow to be productive immediately.

1) High-level architecture (must follow)
- Layer ordering: UI (CustomTkinter panels) → Core (managers) → Models (dataclasses) → Utils (helpers). Keep imports flowing downward only.
- Central config: use `config/settings.py` for paths and constants (e.g. `PROFILES_DIR`, `DOWNLOADS_DIR`, account file names).

2) Key invariants and patterns
- JSON persistence: `data/suno_accounts.json` uses the account name as the JSON key ("name-as-key"). When loading inject key into model; when saving remove it from the value.
- Managers: singletons are created in the UI bootstrap (conceptually `MainWindow.__init__`) and injected into panels. Do not instantiate managers inside UI panels.

3) Browser/session automation
- Chrome profile-based sessions live under `profiles/<account>/` — session extraction and token logic depend on that directory layout. Inspect `legacy_modules/` and `src/core` for session helpers.
- For automating React-controlled inputs, prefer the native setter + synthetic events pattern used in `legacy_modules/suno_auto_create.py` rather than naive send_keys or click sequences.

4) Concurrency and long-running work
- Long tasks (browser launches, batch downloads/creates) run on background threads; managers emit progress callbacks consumed by UI panels. Preserve callback signatures when changing managers.

5) Developer workflows & commands
- Create venv and install: `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1` and `pip install -r requirements.txt`.
- Run GUI smoke: `python app.py`.
- Run/inspect legacy CLI: `python legacy_modules/suno_batch_download.py --help` or `python legacy_modules/suno_multi_account.py`.
- Tests: `pytest` (mock Selenium, file and network I/O in tests/).

6) Files and places to check first (fast map)
- Entry/UI: `app.py`, `src/ui/`
- Core/business logic: `src/core/` (account, session, download managers)
- Config and selectors: `config/settings.py`, `config/suno_selectors_from_clicknium.py`
- Legacy automation: `legacy_modules/suno_auto_create.py`, `legacy_modules/suno_batch_download.py`
- Persistence and state: `data/suno_accounts.json`, `profiles/`, `downloads/`
- Project memory & tasks: `memory-bank/` (read `activeContext.md` and `tasks/_index.md` before edits)

7) Project-specific rules you must not change silently
- Never change the JSON shape for `data/suno_accounts.json` without updating both load/save paths and any code that relies on the name-as-key convention.
- Never import across layers (e.g., UI → Models) — always go through Core managers.

8) Documentation & task hygiene
- When making changes, update `memory-bank/` (task file and `_index.md`) to record context and decisions so future agents can resume safely.

If anything above is unclear or you'd like examples (JS input setter snippet, a small unit test template, or a sample manager constructor), tell me which piece and I will expand it with code and a quick verification test.

### Appendix: React-controlled input (native setter) example
When interacting with React-controlled inputs, do not rely on simple `.value = ...` in all cases. Use the native setter pattern so React's internal change handlers pick up the change. Example (Selenium):

```python
# Example: set value on an <input> or <textarea> and dispatch an input event so React sees it
script = """
const el = arguments[0];
const value = arguments[1];
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set ||
                                         Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
if (nativeSetter) {
    nativeSetter.call(el, value);
} else {
    el.value = value;
}
el.dispatchEvent(new Event('input', { bubbles: true }));
el.dispatchEvent(new Event('change', { bubbles: true }));
"""

# Usage in Python/Selenium
driver.execute_script(script, element, "desired text")
```

The codebase already uses similar patterns (see `legacy_modules/suno_auto_create.py` where sliders and inputs are set via `execute_script(...)` and `dispatchEvent(new Event('input', { bubbles: true }))`). Prefer the native setter variant above when React updates are required.
```
            return cookie['value']  # JWT token
