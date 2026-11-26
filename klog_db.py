#!/usr/bin/env python3
import argparse
import json
import sqlite3
import subprocess
from pathlib import Path

DB_PATH = Path.home() / "scripts" / "logs" / "kernel_events.db"

def init_db(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cursor TEXT UNIQUE,
            timestamp_us INTEGER,
            priority TEXT,
            subsystem TEXT,
            message TEXT
        )
    """)
    conn.commit()

def sync_logs(conn: sqlite3.Connection):
    cmd = ["journalctl", "-k", "-p", "warning", "--since", "24 hours ago", "-o", "json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        print(f"Error reading journal: {res.stderr.strip()}")
        return

    inserted = 0
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        cursor = entry.get("__CURSOR")
        ts = int(entry.get("__REALTIME_TIMESTAMP", 0))
        prio = str(entry.get("PRIORITY", "4"))
        subsys = entry.get("_KERNEL_SUBSYSTEM") or entry.get("SYSLOG_IDENTIFIER") or "kernel"
        msg = entry.get("MESSAGE", "")

        # INSERT OR IGNORE skips duplicate entries automatically using the UNIQUE cursor
        cur = conn.execute(
            "INSERT OR IGNORE INTO events (cursor, timestamp_us, priority, subsystem, message) VALUES (?, ?, ?, ?, ?)",
            (cursor, ts, prio, subsys, str(msg)),
        )
        inserted += cur.rowcount

    conn.commit()
    print(f"Sync complete: {inserted} new kernel event(s) saved to {DB_PATH}")

def query_stats(conn: sqlite3.Connection):
    print("\n=== Top Kernel Subsystems in SQLite Database ===")
    rows = conn.execute("""
        SELECT subsystem, COUNT(*) as total
        FROM events
        GROUP BY subsystem
        ORDER BY total DESC
        LIMIT 5
    """).fetchall()

    if not rows:
        print("No events recorded in database yet.")
        return

    for subsys, total in rows:
        print(f"  {subsys:<15} : {total} event(s)")

def main():
    parser = argparse.ArgumentParser(description="SQLite Kernel Event Logger")
    parser.add_argument("command", choices=["sync", "stats"], help="'sync' imports recent logs; 'stats' runs SQL summary")
    args = parser.parse_args()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        if args.command == "sync":
            sync_logs(conn)
        elif args.command == "stats":
            query_stats(conn)

if __name__ == "__main__":
    main()

