#!/usr/bin/env python3
"""
Sync a todo-list JSON to memory-bank task markdown files and update tasks/_index.md.

Usage:
  python tools/sync_todos.py path/to/todos.json

todos.json format: an array of objects with fields:
  id: integer
  title: string
  description: string
  status: string (Pending | In Progress | Completed | Abandoned)
  added: optional ISO date string
  updated: optional ISO date string

This script will create or update files under memory-bank/tasks/TASK{ID:03d}-{slug}.md
and regenerate memory-bank/tasks/_index.md grouping tasks by status.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from datetime import datetime


BASE = Path(__file__).resolve().parents[1]
TASKS_DIR = BASE / 'memory-bank' / 'tasks'
INDEX_FILE = TASKS_DIR / '_index.md'


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip('-')[:50]


TEMPLATE = """# TASK{tid:03d} - {title}

**Status:** {status}  
**Added:** {added}  
**Updated:** {updated}

## Original Request
{description}

## Thought Process

## Implementation Plan

## Progress Tracking

**Overall Status:** {status}

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|

## Progress Log
### {date}
- Created/Updated by sync_todos.py: status set to {status}

"""


def load_todos(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def write_task_file(task: dict):
    tid = int(task['id'])
    title = task['title']
    status = task.get('status', 'Pending')
    desc = task.get('description', '')
    added = task.get('added') or datetime.utcnow().strftime('%Y-%m-%d')
    updated = datetime.utcnow().strftime('%Y-%m-%d')

    slug = slugify(title)
    fname = TASKS_DIR / f"TASK{tid:03d}-{slug}.md"

    content = TEMPLATE.format(tid=tid, title=title, status=status, added=added, updated=updated, description=desc, date=updated)

    if fname.exists():
        # append progress log entry
        txt = fname.read_text(encoding='utf-8')
        # replace Status / Updated fields
        txt = re.sub(r"\*\*Status:\*\*.*\n", f"**Status:** {status}  \n", txt, count=1)
        txt = re.sub(r"\*\*Updated:\*\*.*\n", f"**Updated:** {updated}\n", txt, count=1)
        # append new progress log entry
        txt += f"\n### {updated}\n- Synchronized: status set to {status}\n"
        fname.write_text(txt, encoding='utf-8')
        return fname

    fname.write_text(content, encoding='utf-8')
    return fname


def regenerate_index():
    # Collect task files
    tasks = []
    for p in sorted(TASKS_DIR.glob('TASK*.md')):
        if p.name == '_index.md':
            continue
        text = p.read_text(encoding='utf-8')
        # parse header
        first_line = text.splitlines()[0].strip()
        m = re.match(r"# TASK(\d{3}) - (.*)", first_line)
        if not m:
            continue
        tid = m.group(1)
        title = m.group(2).strip()
        status_match = re.search(r"\*\*Status:\*\*\s*(.*)", text)
        status = status_match.group(1).strip() if status_match else 'Pending'
        tasks.append({'id': int(tid), 'title': title, 'status': status})

    sections = {'In Progress': [], 'Pending': [], 'Completed': [], 'Abandoned': []}
    for t in tasks:
        s = t['status']
        if 'in progress' in s.lower():
            sections['In Progress'].append(t)
        elif 'pending' in s.lower():
            sections['Pending'].append(t)
        elif 'completed' in s.lower():
            sections['Completed'].append(t)
        elif 'abandoned' in s.lower():
            sections['Abandoned'].append(t)
        else:
            sections['Pending'].append(t)

    lines = ['````markdown', '# Tasks Index', '', '## In Progress', '']
    if sections['In Progress']:
        for t in sections['In Progress']:
            lines.append(f"- [TASK{t['id']:03d}] {t['title']}")
    else:
        lines.append('*No tasks currently in progress*')

    lines += ['', '## Pending', '']
    if sections['Pending']:
        for t in sections['Pending']:
            lines.append(f"- [TASK{t['id']:03d}] {t['title']}")
    else:
        lines.append('*No pending tasks*')

    lines += ['', '## Completed', '']
    if sections['Completed']:
        for t in sections['Completed']:
            lines.append(f"- [TASK{t['id']:03d}] {t['title']}")
    else:
        lines.append('*No completed tasks*')

    lines += ['', '## Abandoned', '']
    if sections['Abandoned']:
        for t in sections['Abandoned']:
            lines.append(f"- [TASK{t['id']:03d}] {t['title']}")
    else:
        lines.append('*No abandoned tasks*')

    lines.append('\n---\n')
    lines.append('\n*This index is automatically updated as tasks are created, updated, and completed.*')
    lines.append('\n````')

    INDEX_FILE.write_text('\n'.join(lines), encoding='utf-8')
    return INDEX_FILE


def main(argv):
    if len(argv) < 2:
        print('Usage: sync_todos.py path/to/todos.json')
        return 2

    path = Path(argv[1])
    if not path.exists():
        print('File not found:', path)
        return 2

    todos = load_todos(path)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    for t in todos:
        write_task_file(t)

    idx = regenerate_index()
    print('Regenerated index at', idx)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
