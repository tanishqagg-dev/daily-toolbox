"""Discover behavior tests, reject empty suites, then check Python syntax."""
import compileall
from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
suite = unittest.defaultTestLoader.discover(str(root / "tests"), top_level_dir=str(root))
if suite.countTestCases() < 1:
    raise SystemExit("No tests discovered")
result = unittest.TextTestRunner(verbosity=2).run(suite)
compiled = all(compileall.compile_dir(str(root / name), quiet=1) for name in ["tools", "tests"])
raise SystemExit(0 if result.wasSuccessful() and compiled else 1)
