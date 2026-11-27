#!/bin/sh
set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BIN_DIR="$HOME/.local/bin"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "=== Setting up Cross-Distro Kernel & Security Scripts ==="

# 1. Auto-detect Debian (apt) vs Fedora (dnf)
if command -v apt-get >/dev/null 2>&1; then
    echo "Detected Debian/Ubuntu (apt)..."
    sudo apt-get update && sudo apt-get install -y \
        shellcheck jq curl libnotify-bin python3 python3-cryptography python3-argon2
elif command -v dnf >/dev/null 2>&1; then
    echo "Detected Fedora/RHEL (dnf)..."
    sudo dnf install -y \
        ShellCheck jq curl libnotify python3 python3-cryptography python3-argon2-cffi
else
    echo "Error: Unsupported package manager (requires apt-get or dnf)." >&2
    exit 1
fi

# 2. Make scripts executable and symlink into ~/.local/bin (SELinux-safe on Fedora)
mkdir -p "$BIN_DIR"
chmod +x "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR"/*.py

for file in "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR"/*.py; do
    name=$(basename "$file")
    [ "$name" = "install.sh" ] && continue
    ln -sfn "$file" "$BIN_DIR/$name"
done

# 3. Configure user-level systemd service and daily timer
mkdir -p "$SYSTEMD_USER_DIR"

cat << UNIT > "$SYSTEMD_USER_DIR/klog-check.service"
[Unit]
Description=Daily Kernel Log Error Check

[Service]
Type=oneshot
ExecStart=$BIN_DIR/klog_check.sh
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

echo "Setup complete! Scripts linked in $BIN_DIR and daily timer enabled."


