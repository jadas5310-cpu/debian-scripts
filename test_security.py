#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path
import hash_guard

class TestHashGuard(unittest.TestCase):
    def test_file_hash_changes_on_modification(self):
        # Create an isolated temporary directory that cleans itself up automatically
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "config.txt"
            test_file.write_text("original safe data", encoding="utf-8")

            hash_before = hash_guard.hash_file(test_file)

            # Simulate unauthorized tampering
            test_file.write_text("tampered malicious data", encoding="utf-8")
            hash_after = hash_guard.hash_file(test_file)

            self.assertNotEqual(hash_before, hash_after)
            self.assertEqual(len(hash_before), 64)  # SHA-256 hex digest is always 64 chars

    def test_scan_directory_ignores_git_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "script.py").write_text("print('hi')", encoding="utf-8")
            git_dir = root / ".git"
            git_dir.mkdir()
            (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

            baseline = root / ".hash_baseline.json"
            results = hash_guard.scan_directory(root, baseline)

            self.assertIn("script.py", results)
            self.assertNotIn(".git/HEAD", results)

if __name__ == "__main__":
    unittest.main(verbosity=2)

