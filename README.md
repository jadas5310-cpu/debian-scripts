# Cross-Distro Linux Kernel, System & Security Scripts

POSIX shell and Python utilities built on **Debian 13 (Trixie)** and tested on **Fedora** to monitor kernel logs, store events in SQLite, encrypt sensitive files, and audit local security.

## Installation

### Option 1: Automated Setup (`Debian / Ubuntu` & `Fedora / RHEL`)
The `install.sh` script automatically detects `apt-get` or `dnf`, installs required system packages, symlinks executables into `~/.local/bin` (SELinux-compatible), and enables the daily `systemd` user timer:

```bash
chmod +x install.sh
./install.sh
```

### Option 2: Install Python CLI Tools via `pipx` (Any Linux Distro)
Install `kquery`, `klog-db`, `hash-guard`, `secret-box`, and `security-report` in an isolated environment:

```bash
pipx install .
```

## Shell & Setup Scripts

* **`install.sh`** — Cross-distro setup script supporting both `apt` and `dnf`, symlinking tools to `~/.local/bin` and configuring `systemd` timers.
* **`sysinfo.sh`** — Quick host, kernel version, and uptime summary.
* **`klog_check.sh`** — Daily kernel error scanner with 30-day log rotation and desktop notifications (`notify-send`).
* **`klog_watch.sh`** — Real-time kernel log keyword filter.
* **`log_tally.lua`**— Lightweight Lua 5.4 stream processor that tallies kernel keyword occurrences from standard input.

## Python Monitoring & Security Utilities

* **`parse_klogs.py`** — Converts saved error reports into a structured `summary.json` file.
* **`live_kstats.py`** — Summarizes 7-day kernel warnings by severity and subsystem.
* **`klog_web.py`** — Serves a local auto-refreshing dark-mode web dashboard at `http://127.0.0.1:8080`.
* **`kquery.py`** — Interactive CLI log search tool with `--level`, `--since`, and `--keyword` ANSI highlighting.
* **`klog_db.py`** — Stores deduplicated kernel events in a local SQLite database (`kernel_events.db`) and runs SQL summary queries.
* **`hash_guard.py`** — SHA-256 file integrity checker that saves baseline snapshots and alerts on modified, added, or deleted files.
* **`secret_box.py`** — Local file and note encryption vault powered by **Argon2id** key derivation and **AES-256-GCM**.
* **`security_report.py`** — Unified security audit report combining SHA-256 integrity checks, failed authentication log scans, and SQLite kernel error counts.
* **`test_security.py`** — Automated `unittest` suite verifying SHA-256 file integrity detection and directory exclusions.

## Quick Usage

```bash
# Run automated unit tests
python3 -m unittest test_security.py -v

# Sync kernel events to SQLite and view top subsystems
klog_db.py sync && klog_db.py stats

# Encrypt or decrypt a sensitive file
secret_box.py lock secret.txt
secret_box.py unlock secret.txt.vault

# Run the unified security audit
security_report.py
```
# Tally recent kernel log keywords with Lua
journalctl -k -n 200 --no-pager | log_tally.lua



