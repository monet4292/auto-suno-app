"""
Smoke test script: launch app.py, wait briefly for the app logger to emit
"Application started", then terminate the process.

This is a lightweight headless-friendly smoke check: it looks for the
log entry written by `src.utils.logger.logger` and also watches stdout.

Exit codes:
 - 0: success (Application started detected)
 - 2: failure (not detected)
"""
from __future__ import annotations
import subprocess
import sys
import time
from pathlib import Path
import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_PY = REPO_ROOT / "app.py"
LOG_DIR = REPO_ROOT / "logs"
LOG_FILE = LOG_DIR / f"app_{datetime.date.today().strftime('%Y%m%d')}.log"

TIMEOUT_SECONDS = 15


def run_smoke():
    if not APP_PY.exists():
        print(f"ERROR: {APP_PY} not found")
        return 2

    # Start the app as subprocess
    proc = subprocess.Popen(
        [sys.executable, str(APP_PY)],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    deadline = time.time() + TIMEOUT_SECONDS
    found = False

    try:
        # Poll stdout and log file for the marker
        while time.time() < deadline:
            # Check stdout if available
            if proc.stdout:
                try:
                    # Non-blocking readline; if empty, continue
                    line = proc.stdout.readline()
                except Exception:
                    line = ""
                if line:
                    print(f"[app stdout] {line.strip()}")
                    if "Application started" in line:
                        found = True
                        break

            # Check log file
            if LOG_FILE.exists():
                try:
                    txt = LOG_FILE.read_text(encoding='utf-8', errors='ignore')
                    if "Application started" in txt:
                        found = True
                        break
                except Exception:
                    pass

            time.sleep(0.3)
    finally:
        # Terminate the app process
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    if found:
        print("SMOKE OK: Application started detected")
        return 0
    else:
        print("SMOKE FAIL: Application started not detected")
        return 2


if __name__ == '__main__':
    sys.exit(run_smoke())
