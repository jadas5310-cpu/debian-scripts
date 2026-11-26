#!/bin/sh
set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "=== Setting up Debian 13 Kernel Scripts ==="

# 1. Install required Debian packages
echo "Checking and installing dependencies..."
sudo apt update && sudo apt install -y shellcheck jq curl libnotify-bin python3

# 2. Ensure all shell and Python scripts are executable
chmod +x "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR"/*.py

# 3. Configure user-level systemd service and daily timer
mkdir -p "$SYSTEMD_USER_DIR"

cat << UNIT > "$SYSTEMD_USER_DIR/klog-check.service"
[Unit]
Description=Daily Kernel Log Error Check

[Service]
Type=oneshot
ExecStart=$SCRIPT_DIR/klog_check.sh
UNIT

cat << TIMER > "$SYSTEMD_USER_DIR/klog-check.timer"
[Unit]
Description=Run Kernel Log Check Daily

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
TIMER

# 4. Reload and enable the timer
systemctl --user daemon-reload
systemctl --user enable --now klog-check.timer

echo "Setup complete! Daily timer is active."


