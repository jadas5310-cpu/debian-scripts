#!/usr/bin/env python3
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path.home() / "scripts"
DB_PATH = SCRIPTS_DIR / "logs" / "kernel_events.db"

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("==================================================")
    print(f"  DEBIAN 13 UNIFIED SECURITY AUDIT ({now})")
    print("==================================================\n")

    # 1. Verify SHA-256 file integrity on ~/scripts
    print("[1] File Integrity Check (~/scripts):")
    hg = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "hash_guard.py"), "check", "-d", str(SCRIPTS_DIR)],
        capture_output=True, text=True, check=False,
    )
    print(" ", hg.stdout.strip().replace("\n", "\n  "))

    # 2. Check failed SSH/sudo authentication attempts in the last 24h
    print("\n[2] Failed Authentication Attempts (Last 24h):")
    auth = subprocess.run(
        ["journalctl", "--since", "24 hours ago", "-g", "Failed password|authentication failure", "--no-pager"],
        capture_output=True, text=True, check=False,
    )
    lines = [l for l in auth.stdout.splitlines() if "No entries" not in l and l.strip()]
    print(f"  {len(lines)} failed authentication event(s) detected.")

    # 3. Query total recorded kernel errors from your SQLite database
    print("\n[3] Kernel Event Database Summary:")
    if DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            total = conn.execute("SELECT COUNT(*) FROM events").fetchone()
            errs = conn.execute("SELECT COUNT(*) FROM events WHERE priority <= '3'").fetchone()
            print(f"  Total stored events: {total} | Critical/Error events: {errs}")
    else:
        print("  Database not initialized yet (run 'klog_db.py sync').")

if __name__ == "__main__":
    main()

