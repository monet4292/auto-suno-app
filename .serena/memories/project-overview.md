# Auto-Suno-App Overview
- **Purpose**: Desktop Suno Account Manager v2.x that automates account/session/queue management, multi-account batch song creation, download orchestration, and history tracking with stealth browser automation.
- **Architecture**: Clean Architecture with 4 layers: UI (`src/ui` CustomTkinter tabs), Core/application services (`src/core` managers), Domain models (`src/models`), and Infrastructure/utilities (`src/utils`). UI depends downward only.
- **Key features**: Multi-queue execution, Chrome-based session persistence, batch download with metadata, anti-CAPTCHA stealth driver, creation/download history with CSV export, and custom styling from `config/`.
- **Primary tech**: Python 3.10+, CustomTkinter GUI, Selenium-style stealth driver, pytest for tests, JSON persistence under `data/`.
- **Entry files**: `app.py` launches GUI; legacy CLI tools live in `legacy_modules/`.
- **Data/logs**: Runtime JSON, profiles, downloads, and logs stored under gitignored folders (`data/`, `profiles/`, `downloads/`, `logs/`).