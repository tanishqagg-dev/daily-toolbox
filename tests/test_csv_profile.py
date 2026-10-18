import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.csv_profile import profile_csv


class CsvProfileTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "sample data.csv"

    def profile(self, content):
        self.path.write_bytes(content.encode("utf-8"))
        return profile_csv(self.path)

    def cli(self):
        return subprocess.run(
            [sys.executable, "-m", "tools.csv_profile", str(self.path)],
            capture_output=True, text=True,
        )

    def test_counts_and_types(self):
        result = self.profile("id,score,active,note,empty\n1,2.5,true,hello,\n2,3,FALSE,4,  \n")
        self.assertEqual(result, {
            "row_count": 2,
            "column_names": ["id", "score", "active", "note", "empty"],
            "missing_cell_counts": [0, 0, 0, 0, 2],
            "inferred_types": ["integer", "number", "boolean", "string", "unknown"],
        })

    def test_quoted_commas_newlines_and_escaped_quotes(self):
        result = self.profile('name,note\r\n"Ada, River","said ""hello""\r\nagain"\r\n')
        self.assertEqual(result["row_count"], 1)
        self.assertEqual(result["missing_cell_counts"], [0, 0])
        self.assertEqual(result["inferred_types"], ["string", "string"])

    def test_bom(self):
        result = self.profile("\ufeffname,count\nAda,1\n")
        self.assertEqual(result["column_names"], ["name", "count"])

    def test_empty_files(self):
        for content in ("", "\ufeff", "\n\r\n"):
            with self.subTest(content=content):
                self.assertEqual(self.profile(content), {
                    "row_count": 0, "column_names": [],
                    "missing_cell_counts": [], "inferred_types": [],
                })

    def test_header_only_and_duplicate_empty_names(self):
        result = self.profile("name,name,\n")
        self.assertEqual(result["column_names"], ["name", "name", ""])
        self.assertEqual(result["row_count"], 0)
        self.assertEqual(result["missing_cell_counts"], [0, 0, 0])
        self.assertEqual(result["inferred_types"], ["unknown"] * 3)

    def test_blank_records_ignored_but_empty_cells_count(self):
        result = self.profile('\nvalue\n\n""\n   \n0\n')
        self.assertEqual(result["row_count"], 3)
        self.assertEqual(result["missing_cell_counts"], [2])
        self.assertEqual(result["inferred_types"], ["integer"])

    def test_type_promotion_and_numeric_grammar(self):
        for values, expected in (
            (["-12", "+003"], "integer"),
            (["1", "2e3", ".5", "-1."], "number"),
            ([".5", "1"], "number"),
            (["true", "1"], "string"),
            (["NaN", "1"], "string"),
            (["2026-10-19"], "string"),
            (["null", "NA"], "string"),
            ([" true ", "FALSE"], "boolean"),
        ):
            with self.subTest(values=values):
                self.assertEqual(self.profile("value\n" + "\n".join(values))["inferred_types"], [expected])

    def test_cli_ragged_rows(self):
        for row, count in (("1", 1), ("1,2,3", 3)):
            with self.subTest(row=row):
                self.path.write_text("a,b\n" + row + "\n", encoding="utf-8")
                result = self.cli()
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn(f"line 2: expected 2 cells, got {count}", result.stderr)

    def test_cli_malformed_quotes(self):
        for content in ('a,b\n1,"unfinished\n', 'a,b\n1,"value"oops\n'):
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                result = self.cli()
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn("line 2: invalid CSV", result.stderr)

    def test_error_line_after_multiline_record(self):
        with self.assertRaisesRegex(ValueError, "line 4: expected 2 cells, got 1"):
            self.profile('a,b\n1,"two\nlines"\nwrong\n')

    def test_cli_invalid_utf8(self):
        self.path.write_bytes(b"name\n\xff\n")
        result = self.cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("csv-profile:", result.stderr)
        self.assertIn("decode", result.stderr)

    def test_cli_missing_file(self):
        result = self.cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("csv-profile:", result.stderr)

    def test_cli_sample_and_no_mutation(self):
        data = Path("examples/csv_profile.csv").read_bytes()
        self.path.write_bytes(data)
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {
            "row_count": 3,
            "column_names": ["name", "visits", "score", "active", "note"],
            "missing_cell_counts": [0, 1, 1, 0, 1],
            "inferred_types": ["string", "integer", "number", "boolean", "string"],
        })
        self.assertEqual(self.path.read_bytes(), data)

    def test_stream_is_iterated_without_bulk_reads(self):
        class LinesOnly:
            def __enter__(self):
                return iter(["value\n", "1\n", "2\n"])

            def __exit__(self, *args):
                pass

        with patch.object(Path, "open", return_value=LinesOnly()):
            self.assertEqual(profile_csv(self.path)["row_count"], 2)

    def test_oversized_field_is_data_error(self):
        with self.assertRaisesRegex(ValueError, "invalid CSV: field larger"):
            self.profile("value\n" + "x" * (csv.field_size_limit() + 1))


if __name__ == "__main__":
    unittest.main()
