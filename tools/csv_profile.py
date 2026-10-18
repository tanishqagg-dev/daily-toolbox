"""Profile a UTF-8 CSV file as JSON. Run with python -m tools.csv_profile."""
import argparse
import csv
import json
from pathlib import Path
import re
import sys


INTEGER = re.compile(r"[+-]?[0-9]+\Z")
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def cell_type(value):
    if value.lower() in {"true", "false"}:
        return "boolean"
    if INTEGER.fullmatch(value):
        return "integer"
    if NUMBER.fullmatch(value):
        return "number"
    return "string"


def merge_types(previous, current):
    if previous == "unknown" or previous == current:
        return current
    if {previous, current} <= {"integer", "number"}:
        return "number"
    return "string"


def profile_csv(path):
    """Read one record at a time; retain only per-column counts and types."""
    result = {"row_count": 0, "column_names": [], "missing_cell_counts": [], "inferred_types": []}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        has_header = False
        try:
            for row in reader:
                if not row:
                    continue
                if not has_header:
                    result["column_names"] = row
                    result["missing_cell_counts"] = [0] * len(row)
                    result["inferred_types"] = ["unknown"] * len(row)
                    has_header = True
                    continue
                width = len(result["column_names"])
                if len(row) != width:
                    raise ValueError(
                        f"line {reader.line_num}: expected {width} cells, got {len(row)}"
                    )
                result["row_count"] += 1
                for index, value in enumerate(row):
                    value = value.strip()
                    if not value:
                        result["missing_cell_counts"][index] += 1
                    else:
                        result["inferred_types"][index] = merge_types(
                            result["inferred_types"][index], cell_type(value)
                        )
        except csv.Error as exc:
            raise ValueError(f"line {reader.line_num}: invalid CSV: {exc}") from exc
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        result = profile_csv(args.file)
    except (OSError, UnicodeError, ValueError) as exc:
        print("csv-profile: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
