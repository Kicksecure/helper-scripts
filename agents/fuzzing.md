## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

# Fuzzing

Two layers, in increasing depth:

## 1. Hypothesis property tests

Live in `ci/tests/<pkg>/test_property.py`. **Outside** the Python
package tree on purpose: `debian/helper-scripts.install` ships
`usr/*`, so keeping property tests under `ci/tests/` means they do
NOT end up in the installed `.deb`. The original (non-Hypothesis)
unit tests still live under `usr/lib/python3/dist-packages/<pkg>/tests/`
because they predate the .deb-shipping concern; only the new
property tests were relocated.

Discovered by `./run-tests` via a separate pytest invocation that
cd's into each `ci/tests/<pkg>/` and runs
`pytest --import-mode=importlib`. Run as part of the lint workflow.

Local run (single package):
```
PYTHONPATH=usr/lib/python3/dist-packages \
  python3 -m pytest --import-mode=importlib \
    ci/tests/stdisplay/test_property.py
```

When adding a new package, add a `ci/tests/<pkg>/test_property.py`
with three properties: `test_never_raises`, `test_idempotent` (if
applicable), and one domain-specific invariant. Add the package to
the `py_lib_to_test_list` in `run-tests`.

## 2. ClusterFuzzLite (Atheris under the hood)

Coverage-guided fuzzing of Python harnesses, orchestrated by
ClusterFuzzLite. Atheris is the engine; ClusterFuzzLite handles the
build (OSS-Fuzz base-builder + `compile_python_fuzzer`), corpus
persistence (via `actions/cache`), crash dedup, SARIF, and PR
annotations.

Harnesses live in `fuzz/fuzz_<pkg>.py`. Configuration:
`.clusterfuzzlite/{Dockerfile,build.sh,project.yaml}`.

Workflow: `.github/workflows/fuzz.yml` with two jobs in one file:
- `pr` - short fuzz on every PR that touches the Python packages
  or harnesses. Findings appear as PR annotations.
- `batch` - longer-budget batch fuzz on schedule + workflow_dispatch.
  Crashes / corpora persist via `actions/cache`.

Local run against a single harness (no docker, no ClusterFuzzLite -
direct Atheris invocation, useful for iterating on a new harness):
```
python3 fuzz/fuzz_stdisplay.py -max_total_time=60
```
(Requires `pip install atheris` plus the package's runtime deps;
the workflow does this in the OSS-Fuzz base-builder image.)

Adding a harness: drop a new `fuzz/fuzz_<pkg>.py` next to the
existing harnesses. `.clusterfuzzlite/build.sh` loops
`compile_python_fuzzer` over every `fuzz/fuzz_*.py`, so it's
picked up automatically.

## Trust footprint

- Hypothesis: Debian apt (`python3-hypothesis`).
- ClusterFuzzLite + Atheris + OSS-Fuzz base-builder: Google. Per-pin
  provenance is in `.github/workflows/fuzz.yml` and
  `.clusterfuzzlite/Dockerfile`, not duplicated here.
