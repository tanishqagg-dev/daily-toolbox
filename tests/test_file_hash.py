import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.file_hash import sha256_file


class FileHashTests(unittest.TestCase):
    def test_known_sha256(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_file(path), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty"
            path.touch()
            self.assertEqual(sha256_file(path), hashlib.sha256(b"").hexdigest())

    def test_multiple_chunks_and_no_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "binary"
            data = bytes(range(256)) * 9000
            path.write_bytes(data)
            self.assertEqual(sha256_file(path), hashlib.sha256(data).hexdigest())
            self.assertEqual(path.read_bytes(), data)

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "has spaces.txt"
            path.write_bytes(b"abc")
            result = subprocess.run([sys.executable, "-m", "tools.file_hash", str(path), "--json"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["sha256"], hashlib.sha256(b"abc").hexdigest())

    def test_cli_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, "-m", "tools.file_hash", str(Path(folder) / "missing")],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("file-hash:", result.stderr)


if __name__ == "__main__":
    unittest.main()
