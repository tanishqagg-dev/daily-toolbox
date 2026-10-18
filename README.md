# Daily toolbox

Small command-line tools for files, text and data. Python 3.11 or newer. No third-party packages.

## File hash

Print a SHA-256 digest without loading the file into memory.

```sh
python3 -m tools.file_hash README.md
python3 -m tools.file_hash README.md --json
```

## CSV profiler

Print row count, column names, missing-cell counts and inferred types as JSON.
The input is read one record at a time and is never modified.

```sh
python3 -m tools.csv_profile examples/csv_profile.csv
python3 -m tools.csv_profile examples/csv_profile.csv | python3 -m json.tool
```

The synthetic sample includes a quoted comma and a multiline cell. It produces:

```json
{"row_count": 3, "column_names": ["name", "visits", "score", "active", "note"], "missing_cell_counts": [0, 1, 1, 0, 1], "inferred_types": ["string", "integer", "number", "boolean", "string"]}
```

- Input must be UTF-8; an initial BOM is accepted. The first nonblank record is
  the header. Names are preserved, including duplicate and empty names. All output
  arrays use header order.
- Blank records are ignored. A quoted empty cell or a whitespace-only cell counts
  as missing. Literal `null` and `NA` are strings. The header is excluded from the
  row count.
- Types ignore surrounding whitespace. `true` and `false` are booleans regardless
  of case. Signed ASCII digits are integers, including leading zeros. Decimals and
  scientific notation are numbers. Integers mixed with numbers become `number`;
  other mixed types become `string`. Dates, `NaN` and infinity are strings.
  Columns with no nonmissing values have type `unknown`.
- Empty files produce zero rows and empty arrays. Header-only files produce zero
  counts and `unknown` types for each column.
- Parsing uses Python's strict CSV reader with commas, double-quoted fields and
  doubled quote escapes. Quotes inside unquoted fields are treated as literal
  characters. Unterminated quoted fields and text after a closing quote are errors.
  The standard reader's field-size limit applies, normally 131072 characters.
- Rows with too few or too many cells and CSV syntax errors report the physical
  line where the error was detected. Invalid UTF-8 and file access errors also
  fail. Errors go to stderr with exit status 1 and no JSON on stdout.

Memory use grows with the column count and the largest record, not the file's
total row count.

## Run the tests

```sh
python3 scripts/verify.py
```

## How changes arrive

A local daily Codex automation adds a useful tool or improves an existing one.
Each change goes through a pull request, local tests and GitHub CI on Python 3.11
and 3.13. The automation merges only after both CI jobs pass for the PR commit.
Generated code and automated commits are part of the repository's normal workflow.
Sample data is synthetic. This repository has no runtime dependencies or secrets.
