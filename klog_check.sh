#!/bin/sh
# Exit immediately if an uninitialized variable is used (-u)
set -u

LOG_DIR="$HOME/scripts/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$LOG_DIR/kernel_report_$TIMESTAMP.txt"
TMP_FILE=$(mktemp)


# Cleanup function triggered automatically on script exit (EXIT) or Ctrl+C (INT/TERM)
# shellcheck disable=SC2317
cleanup() {
    rm -f "$TMP_FILE"
}
trap cleanup EXIT INT TERM

mkdir -p "$LOG_DIR"
# Delete report files older than 30 days (-mtime +30)
find "$LOG_DIR" -name "kernel_report_*.txt" -type f -mtime +30 -delete

# Run journalctl and capture both output and its exit code
if ! journalctl -k -p err --since "24 hours ago" --no-pager > "$TMP_FILE" 2>&1; then
    echo "ERROR: Failed to read kernel journal. Check permissions." >&2
    command -v notify-send >/dev/null 2>&1 && \
        notify-send -u critical "Kernel Monitor Failed" "Could not read journalctl."
    exit 1
fi

# Check if the temp file is empty (-s means file exists and has size > 0)
if [ ! -s "$TMP_FILE" ] || grep -q "No entries" "$TMP_FILE"; then
    echo "Status: HEALTHY. No critical kernel errors found."
    exit 0
else
    COUNT=$(wc -l < "$TMP_FILE")
    echo "Status: WARNING. $COUNT error line(s) detected!"

    {
        echo "=== Debian Kernel Error Report ==="
        echo "Generated: $(date)"
        echo "Kernel Version: $(uname -r)"
        echo "----------------------------------"
        cat "$TMP_FILE"
    } > "$REPORT_FILE"

    # Trigger a critical desktop alert if notify-send is installed
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u critical "Debian Kernel Alert" "$COUNT kernel error(s) logged. Saved to $REPORT_FILE"
    fi

    exit 0
fi


