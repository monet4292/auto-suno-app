## ADDED Requirements

### Requirement: Capability scope and constraints are declared up front
The DocS Migration Checklist SHALL reside at docs/migration-checklist.md, explicitly reference docs/python-to-nodejs-migration-plan.md, and enumerate its canonical sections (Introduction & Scope, Week 0 Preparation, Phases 1-4, Critical Decision Points, Rollback Procedures, Success Validation, Support Contacts). The overview SHALL summarize the 16-week cadence (Week 0 plus four phases), highlight that decision gates, rollback coverage, and validation checklists live in dedicated sections, and call out that all timelines/tasks map back to the `nodejs-backend/` workspace and supporting scripts. The document SHALL forbid embedding sensitive data or raw dumps; instead it MUST direct engineers to gitignored locations (`data/`, `profiles/`, `logs/`, backups) and approved tooling references (npm, pytest, scripts/*.py) when persisting outputs.

#### Scenario: Auditor inspects the checklist scope
- **GIVEN** the auditor opens docs/migration-checklist.md
- **WHEN** they review the intro/table of contents
- **THEN** they see the declared file location, cross-reference to python-to-nodejs-migration-plan.md, the 16-week scope summary with gating/rollback/validation callouts, the list of required sections, and an explicit constraint reminding readers to store backups/baselines in gitignored folders without pasting credentials or data snippets into the checklist.

### Requirement: Migration checklist document exists and frames the full timeline
The project SHALL maintain a docs/migration-checklist.md (aka DocS Migration Checklist) that states the goal of migrating Suno Account Manager from Python to Node.js, cites the 16-week schedule (Week 0 preparation plus Phases 1-4), and explains that the checklist complements python-to-nodejs-migration-plan.md with actionable steps.

#### Scenario: Contributor opens the checklist to understand scope
- **GIVEN** a team member opens docs/migration-checklist.md
- **WHEN** they read the introduction and table headers
- **THEN** they see language that links the checklist to the overall migration effort, mentions the duration (Weeks 0-16), and clarifies that the document is used as an execution tracker aligned with the migration plan.

### Requirement: Pre-migration readiness is fully enumerated
The checklist SHALL provide a "Week 0" section that lists environment setup, backup/snapshot creation, baseline performance capture, and team coordination items, each expressed as checkbox tasks with concrete shell/PowerShell examples (e.g., git branch creation, Node 18 verification, python pytest smoke tests, project backup script).

#### Scenario: Engineer verifies prerequisites before Phase 1
- **GIVEN** an engineer scrolls to the Pre-Migration Preparation block
- **WHEN** they inspect the tasks under Environment Setup, Backup & Safety, and Team Coordination
- **THEN** they find actionable items with code fences showing the necessary commands (git, Node/npm, Python tests, backup copy) plus reminders to document Python baselines and assign responsibilities.

### Requirement: Phased execution details include per-week/day checklists
The document SHALL break Phases 1-4 into Week-level subsections, and each week SHALL contain day-range headers (e.g., "Day 29-31") with checkbox tasks that mention tangible outputs (Express server, SunoApiClient, DownloadManager, Puppeteer setup, Electron UI panels) and validation commands (curl, npm run test:*, pytest).

#### Scenario: Tech lead plans upcoming work
- **GIVEN** the tech lead reviews Phase 2 in the checklist
- **WHEN** they expand the Week 5-8 entries
- **THEN** they observe specific day-group headings with tasks referencing DownloadManager, FileDownloader, QueueManager, and test scripts, plus command/code fences that describe how to verify each deliverable; similar granularity is available for Phases 1, 3, and 4.

### Requirement: Decision gates guard advancement between phases
The checklist SHALL define Go/No-Go checkpoints after Phases 1, 2, and 3 plus a final readiness gate, each outlining success criteria (e.g., Node backend parity, data integrity, CAPTCHA rate <5%, user acceptance) and instructing teams to pause or extend the current phase if criteria fail.

#### Scenario: Program manager evaluates end of Phase 3
- **GIVEN** Phase 3 tasks are completed
- **WHEN** the manager references the "Critical Decision Points" section
- **THEN** they see explicit go/no-go bullets for Phase 3 detailing the CAPTCHA threshold, automation completeness, and the action to extend the phase if metrics are not met.

### Requirement: Rollback coverage spans emergency and planned procedures
The checklist SHALL include both an emergency rollback procedure (immediate shutdown of Node/Electron processes, reactivating the Python stack, verifying health) and a planned rollback procedure at phase boundaries (backup/export steps, service stop commands, Python environment restoration, re-import scripts), each expressed as ordered command blocks.

#### Scenario: On-call engineer needs to revert mid-phase
- **GIVEN** a production issue surfaces during Phase 2
- **WHEN** the engineer visits the Rollback Procedures section
- **THEN** they find two clearly titled subsections (Emergency Rollback, Planned Rollback) with numbered command snippets (pkill node/electron, activate venv, python app.py, scripts/create-backup.sh, node scripts/export-nodejs-data.js, npm run stop, etc.) that guide the reversion.

### Requirement: Success validation checklist enforces testing & documentation
The document SHALL conclude with a "Success Validation" block that restates the tests required per phase (npm run test:unit/integration/performance, pytest integration bridge), manual regression expectations, and documentation update requirements before declaring success.

#### Scenario: QA lead signs off a phase
- **GIVEN** QA is reviewing whether Phase 2 can close
- **WHEN** they consult the Success Validation section
- **THEN** they see checkbox items covering automated tests, performance benchmark comparisons, regression sweeps, and doc updates, enabling them to confirm completion before moving ahead.



