#!/bin/sh

# Allow passing a custom keyword (e.g., klog_watch.sh wifi), or use defaults
PATTERN="${1:-error|fail|warn|usb|bug}"

echo "Watching live kernel logs for: [$PATTERN]"
echo "Press Ctrl+C to stop."
echo "----------------------------------------"

# Stream live kernel messages (-kf), skipping old entries (-n 0)
# grep --line-buffered forces immediate output instead of waiting for a full block
journalctl -kf -n 0 | grep --line-buffered -iE --color=always "$PATTERN"
