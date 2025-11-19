# Phase & Gate Notes (derived from docs/python-to-nodejs-migration-plan.md + docs/migration-checklist.md)

## Week 0 – Preparation
- **Deliverables**: Node.js env setup, branch eature/nodejs-migration, install Node 18+, scaffold 
odejs-backend/, install Express/Axios/Puppeteer deps, create full project backup, capture baseline metrics (python app.py --test-all, pytest, perf stats), assign roles & comms cadence.
- **Gate Criteria**: Branch + environment verified, backups stored under gitignored locations, baseline metrics documented (baseline.md), ownership matrix agreed, kick-off meeting logged. Blockers: Missing baselines or unassigned responsibilities.

## Phase 1 (Weeks 1-4) – API Backend
- **Deliverables**: Express server + health check, SunoApiClient, API directory structure, ESLint/Jest setup, Profile Clips endpoint with pagination, prompt submission APIs, health metrics endpoints, dev workflows (
pm run dev, tests).
- **Gate Criteria**: All API endpoints functionally match Python backend (curl + test scripts), Jest unit/integration suites green, performance acceptable vs baseline, Node server stable. Go/No-Go: “Can Node.js backend replace Python API?”

## Phase 2 (Weeks 5-8) – Core Services & Downloads
- **Deliverables**: DownloadManager/FileDownloader parity, queue orchestration, metadata tagging, batch song creation endpoints, rate limiting guards, persistence bridging, integration tests.
- **Dependencies**: Builds on Phase 1 endpoints.
- **Gate Criteria**: All backend features migrated with no data loss, download throughput + integrity verified, pytest bridges and npm integration tests pass. Go/No-Go: “Can Node.js handle all backend operations?”

## Phase 3 (Weeks 9-12) – Browser Automation (Puppeteer)
- **Deliverables**: Puppeteer-based session manager, anti-CAPTCHA delays, queue automation hooks, monitoring for CAPTCHA rate, recovery scripts, logging integration.
- **Gate Criteria**: CAPTCHA rate <5%, automation flows stable, rollback rehearsed, perf/log targets met. Go/No-Go: “Is Puppeteer automation effective?”

## Phase 4 (Weeks 13-16) – Frontend / Electron UI
- **Deliverables**: Electron shell, React integration, migration of Account/Download/Queue panels, WebSocket progress updates, state management, final UI polish, UAT.
- **Gate Criteria**: Feature parity with Python GUI, WebSocket realtime updates validated, end-to-end + performance + UAT pass, documentation updated. Final readiness includes user acceptance and production checklist.

## Cross-cutting Gates & Rollback
- **Decision Points**: After Weeks 4,8,12,16 with explicit Go/No-Go checklists from docs/migration-checklist.md.
- **Rollback**: Emergency pkill node/electron + python app.py path; planned rollback commands (scripts/create-backup.sh, node scripts/export-nodejs-data.js, npm run stop, venv restore, scripts/import-nodejs-data.py).

## Validation Hooks
- **Tests**: 
pm run test, 
pm run test:unit, 
pm run test:integration, 
pm run test:performance, plus pytest bridging and manual regressions.
- **Success Metrics**: >95% feature parity, zero data loss, performance ≥ baseline, CAPTCHA <5%, user acceptance + monitoring in place.
