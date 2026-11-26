# Debian 13 Kernel & System Scripts

POSIX shell and Python utilities built on Debian 13 (Trixie) to monitor kernel logs and system metrics.

## Scripts
* `sysinfo.sh` - Quick host, kernel, and uptime summary
* `klog_check.sh` - Daily kernel error scanner with log rotation and desktop alerts
* `klog_watch.sh` - Real-time kernel log keyword filter
* `parse_klogs.py` - Converts saved error reports to `summary.json`
* `live_kstats.py` - Summarizes 7-day kernel warnings by severity and subsystem
* `klog_web.py` - Local web dashboard at `http://127.0.0.1:8080`
