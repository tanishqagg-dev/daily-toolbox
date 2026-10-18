# Daily toolbox

Small command-line tools for files, text and data. Python 3.11 or newer. No third-party packages.

## File hash

Print a SHA-256 digest without loading the file into memory.

```sh
python3 -m tools.file_hash README.md
python3 -m tools.file_hash README.md --json
```

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
