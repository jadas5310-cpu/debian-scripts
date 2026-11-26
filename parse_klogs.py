#!/usr/bin/env python3
import json
import re
from pathlib import Path

LOG_DIR = Path.home() / "scripts" / "logs"
OUTPUT_JSON = LOG_DIR / "summary.json"

def parse_reports():
    if not LOG_DIR.exists():
        print("No logs directory found.")
        return

    summary = {
        "total_reports": 0,
        "total_error_lines": 0,
        "reports": []
    }

    # Find all kernel_report_*.txt files sorted chronologically
    for report_path in sorted(LOG_DIR.glob("kernel_report_*.txt")):
        lines = report_path.read_text(encoding="utf-8").splitlines()

        generated = "Unknown"
        kernel = "Unknown"
        error_entries = []

        for line in lines:
            if line.startswith("Generated:"):
                generated = line.split(":", 1)[1].strip()
            elif line.startswith("Kernel Version:"):
                kernel = line.split(":", 1)[1].strip()
            elif not line.startswith(("===", "---")) and line.strip():
                # Extract subsystem tag if present (e.g., 'usb 1-2:', 'nvme 0000:')
                match = re.search(r"kernel:\s+([a-zA-Z0-9_-]+)", line)
                subsystem = match.group(1) if match else "general"
                error_entries.append({
                    "subsystem": subsystem,
                    "raw_message": line
                })

        summary["total_reports"] += 1
        summary["total_error_lines"] += len(error_entries)
        summary["reports"].append({
            "file": report_path.name,
            "generated": generated,
            "kernel": kernel,
            "error_count": len(error_entries),
            "entries": error_entries
        })

    OUTPUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Parsed {summary['total_reports']} report(s) into {OUTPUT_JSON}")

if __name__ == "__main__":
    parse_reports()
