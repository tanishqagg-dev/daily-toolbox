"""Stream a file's SHA-256 digest. Run with python -m tools.file_hash."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        result = sha256_file(args.file)
    except OSError as exc:
        print("file-hash: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"file": str(args.file), "sha256": result}) if args.as_json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
