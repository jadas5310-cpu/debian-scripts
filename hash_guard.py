#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def hash_file(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def scan_directory(target_dir: Path, baseline_path: Path) -> dict:
    hashes = {}
    for path in sorted(target_dir.rglob("*")):
        if path.is_file() and path != baseline_path and ".git" not in path.parts:
            rel_path = str(path.relative_to(target_dir))
            hashes[rel_path] = hash_file(path)
    return hashes

def main():
    parser = argparse.ArgumentParser(description="SHA-256 File Integrity Checker")
    parser.add_argument("action", choices=["init", "check"], help="'init' saves baseline; 'check' verifies files")
    parser.add_argument("-d", "--dir", default=".", help="Directory to monitor (default: current folder)")
    args = parser.parse_args()

    target = Path(args.dir).resolve()
    baseline_file = target / ".hash_baseline.json"

    if args.action == "init":
        hashes = scan_directory(target, baseline_file)
        baseline_file.write_text(json.dumps(hashes, indent=2), encoding="utf-8")
        print(f"Baseline saved for {len(hashes)} file(s) in {baseline_file}")

    elif args.action == "check":
        if not baseline_file.exists():
            print("No baseline found! Run 'hash_guard.py init' first.")
            return

        old_hashes = json.loads(baseline_file.read_text(encoding="utf-8"))
        new_hashes = scan_directory(target, baseline_file)

        modified = [f for f in new_hashes if f in old_hashes and new_hashes[f] != old_hashes[f]]
        added = [f for f in new_hashes if f not in old_hashes]
        deleted = [f for f in old_hashes if f not in new_hashes]

        if not (modified or added or deleted):
            print("STATUS: OK — All files match the SHA-256 baseline.")
        else:
            print("STATUS: ALERT — File changes detected!")
            for f in modified:
                print(f"  [MODIFIED] {f}")
            for f in added:
                print(f"  [ADDED]    {f}")
            for f in deleted:
                print(f"  [DELETED]  {f}")

if __name__ == "__main__":
    main()

