# Debian 13 Kernel & System Scripts

POSIX shell and Python utilities built on Debian 13 (Trixie) to monitor kernel logs, inspect system metrics, and verify file integrity.

## Shell & Setup Scripts

* **`install.sh`** — Automated setup script that installs dependencies and enables the daily `systemd` user timer.
* **`sysinfo.sh`** — Quick host, kernel version, and uptime summary.
* **`klog_check.sh`** — Daily kernel error scanner with 30-day log rotation and desktop notifications (`notify-send`).
* **`klog_watch.sh`** — Real-time kernel log keyword filter.

## Python Utilities

* **`parse_klogs.py`** — Converts saved error reports into a structured `summary.json` file.
* **`live_kstats.py`** — Summarizes 7-day kernel warnings by severity and subsystem.
* **`klog_web.py`** — Serves a local auto-refreshing dark-mode web dashboard at `http://127.0.0.1:8080`.
* **`kquery.py`** — Interactive CLI log search tool with `--level`, `--since`, and `--keyword` ANSI highlighting.
* **`hash_guard.py`** — SHA-256 file integrity checker that saves baseline snapshots and alerts on modified, added, or deleted files.

## Quick Usage



