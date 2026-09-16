<!--
Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
See the file COPYING for copying conditions.
-->

# Agents

Detailed guidance for AI agents working on this codebase.

## Policy

- No unicode. All files must be ASCII-only.

## Reference

- Bash style guide (org-wide; hosted canonically in developer-meta-files):
  https://github.com/Kicksecure/developer-meta-files/blob/master/agents/bash-style-guide.md
- [stdisplay](agents/stdisplay-security.md)
- [Fuzzing](agents/fuzzing.md) - Hypothesis property tests, Atheris harnesses, ClusterFuzzLite
- Shell-invocation guard: python entry points under `usr/bin/` carry a single
  guard line right after the header --
  `"exec" "bash" "-c" "printf '%s\n' '$0: ERROR: Do not execute this script with bash!' >&2; exit 1"`.
  Under python3 it is an inert string-expression statement; if a shell starts
  the script (the `#!/usr/bin/python3` shebang is then ignored) the shell runs
  it, printing the error with the script name and exiting 1 -- refusing rather
  than limping on. This stops the `import` lines below from running as shell
  commands -- `import` is ImageMagick's screen-grab tool (XGrabServer), which
  freezes X. The `interpreter-invocation-guard` hook enforces the same rule at
  the caller side. The pylint-checked entry points (the `utils` in `run-tests`)
  carry a trailing `# pylint: disable=line-too-long` because the fixed idiom
  exceeds the 79-col limit and cannot be wrapped (black leaves it as-is); keep
  that disable. Keep the guard a single line under a terse
  `## Shell-invocation guard.` comment; never re-expand it.
- GUI helpers: any script that builds a QApplication must call `exit_if_no_gui()`
  (`from guimessages.check_display import exit_if_no_gui`) AFTER argparse, BEFORE the QApplication --
  a headless / confined / cron launch otherwise SIGABRTs (exit 134, an uncatchable C++ qFatal).
  It checks DISPLAY / WAYLAND_DISPLAY and honours `QT_QPA_PLATFORM` (offscreen / CI renders are
  NOT suppressed); it exits 0 with a stderr note. Reuse the shared helper -- never duplicate the check.

## Tests

Comprehensive tests + fuzzers for several helper-scripts tools are too
high-volume for human review and live in the AI-maintained dist-ai repo, not
here (https://github.com/org-ai-assisted/dist-ai). Run each against this
checkout:

    SANITIZE_STRING_BIN="$PWD/usr/bin/sanitize-string" sanitize-string-tests    # usr/share/sanitize-string-tests/
    STDISPLAY_REPO="$PWD" stcat-family-tests                                    # usr/share/stcat-family-tests/
    UNICODE_SHOW_REPO="$PWD" unicode-show-tests                                 # usr/share/unicode-show-tests/
    GREP_FIND_UNICODE_WRAPPER_REPO="$PWD" grep-find-unicode-wrapper-tests       # usr/share/grep-find-unicode-wrapper-tests/
    CHECK_REF_COMMITS_REPO="$PWD" check-ref-commits-for-unicode-tests           # usr/share/check-ref-commits-for-unicode-tests/
