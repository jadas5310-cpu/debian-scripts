#!/usr/bin/env python3
import argparse
import re
import subprocess

RED = "\033[1;31m"
RESET = "\033[0m"

def main():
    parser = argparse.ArgumentParser(description="Query and highlight Debian 13 kernel logs.")
    parser.add_argument("-l", "--level", default="warning", help="Log priority (err, warning, info)")
    parser.add_argument("-s", "--since", default="24 hours ago", help="Time window (e.g., '2 hours ago')")
    parser.add_argument("-k", "--keyword", default="", help="Optional keyword to filter and highlight")
    args = parser.parse_args()

    cmd = ["journalctl", "-k", "-p", args.level, "--since", args.since, "--no-pager"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if res.returncode != 0:
        print(f"Error: {res.stderr.strip()}")
        return

    lines = res.stdout.splitlines()
    matches = 0

    for line in lines:
        if args.keyword:
            if args.keyword.lower() not in line.lower():
                continue
            # Highlight matching keyword in bold red
            highlighted = re.sub(
                f"({re.escape(args.keyword)})",
                f"{RED}\\1{RESET}",
                line,
                flags=re.IGNORECASE,
            )
            print(highlighted)
        else:
            print(line)
        matches += 1

    print(f"\n--- Found {matches} matching kernel log line(s) ---")

if __name__ == "__main__":
    main()

