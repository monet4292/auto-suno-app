# Coding Standards
- **Language protocol**: Think in English but respond to user in Vietnamese.
- **Type safety**: Provide exhaustive type hints, avoid `any`/`unknown`; prefer functional style ("no Python classes" unless absolutely required).
- **Hard-coded values**: Disallow unless unavoidable; import shared paths/constants from `config.settings`.
- **Logging**: Always use `src.utils.logger.logger`; never `print` for telemetry.
- **Imports**: Respect downward dependency flow (UI → Core → Models → Utils). No reverse imports.
- **Architecture**: Maintain Clean Architecture separation across layers; uphold module-specific AGENTS.md conventions before editing each area.
- **Docstrings & style**: Python 3.10+, PEP 8, module docstrings required, snake_case functions/vars, PascalCase UI classes, constants UPPER_SNAKE_CASE.
- **State files**: Persist app state via JSON helpers in `src/utils/helpers.py`; avoid duplicating file paths; `data/` contents remain gitignored.
- **Other rules**: Update docs (README, CLAUDE.md, CHANGELOG, docs/, memory-bank) when behavior shifts; keep logger singleton; follow security guidance (no Chrome profiles/token leaks).