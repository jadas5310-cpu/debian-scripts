#!/usr/bin/env python3
import json
import subprocess
from collections import Counter

def get_kernel_stats():
    # Run journalctl outputting one JSON object per line (-o json)
    cmd = ["journalctl", "-k", "-p", "warning", "--since", "7 days ago", "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print(f"Error querying journal: {result.stderr.strip()}")
        return

    subsystems = Counter()
    priorities = Counter()
    # Map numeric syslog priorities to readable labels
    prio_map = {"0": "EMERG", "1": "ALERT", "2": "CRIT", "3": "ERR", "4": "WARN"}

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)

        # Extract priority and hardware subsystem (if available)
        prio = prio_map.get(str(entry.get("PRIORITY")), "OTHER")
        subsys = entry.get("_KERNEL_SUBSYSTEM") or entry.get("SYSLOG_IDENTIFIER") or "kernel"

        priorities[prio] += 1
        subsystems[subsys] += 1

    print("=== 7-Day Kernel Warning & Error Breakdown ===")
    print("By Severity:", dict(priorities))
    print("Top Subsystems:", dict(subsystems.most_common(5)))

if __name__ == "__main__":
    get_kernel_stats()
