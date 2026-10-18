# Daily toolbox

Build small, useful Python command-line tools. Use Python's standard library and
synthetic examples. Keep file operations read-only unless the user explicitly
passes an output path. Never overwrite an existing file without an explicit flag.

Add behavior tests, including subprocess CLI tests and error cases. Run
`python3 scripts/verify.py`. Keep documentation factual and give runnable examples.
Use the unslop writing skill when available. Do not add filler contributions.

The automation may change tools/*.py, tests/test_*.py, README.md, BACKLOG.md,
docs/*.md and examples text files. It must not change this policy, package
initializers, scripts, CI workflows or automation configuration.
