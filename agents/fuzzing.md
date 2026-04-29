## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Authored by Claude (Anthropic).

# Fuzzing

Three layers, in increasing depth:

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

## 2. Atheris harnesses

Live in `fuzz/fuzz_<pkg>.py`. Coverage-guided fuzzing.

Local run (single harness, time-bounded):
```
python3 fuzz/fuzz_stdisplay.py -max_total_time=60
```

Local run (all harnesses, the way CI does it):
```
PYTHON3=python3.13 MAX_TOTAL_TIME=60 bash ci/fuzz-run.sh
```
(`PYTHON3=` only needed if your system `python3` is older than 3.12.)

CI: `.github/workflows/fuzz.yml` runs all harnesses on the weekly
cron and on `workflow_dispatch`. Atheris is installed via
`ci/fuzz-install.sh`.

When adding a new package, add a `fuzz/fuzz_<pkg>.py` next to the
existing harnesses; the CI workflow picks it up automatically.

## 3. ClusterFuzzLite

Continuous fuzzing using OSS-Fuzz infrastructure executed locally
in our GitHub Actions runners.

Configuration: `.clusterfuzzlite/{Dockerfile,build.sh,project.yaml}`.
Workflows:
- `.github/workflows/cflite-pr.yml` - short fuzz on every PR that
  touches the Python packages or harnesses. Findings appear as
  PR annotations.
- `.github/workflows/cflite-batch.yml` - daily batch fuzz with a
  longer per-fuzzer budget. Crashes / corpora persist via
  `actions/cache`.

Adding a harness: same as for Atheris. The build script
(`.clusterfuzzlite/build.sh`) loops `compile_python_fuzzer` over
every `fuzz/fuzz_*.py`.

## Trust footprint

- Hypothesis: Debian apt (`python3-hypothesis`).
- Atheris: Google, PyPI (not in Debian).
- ClusterFuzzLite: Google + OSS-Fuzz. Per-pin provenance is in the
  workflow YAML (`.github/workflows/cflite-*.yml`,
  `.clusterfuzzlite/Dockerfile`), not duplicated here.
