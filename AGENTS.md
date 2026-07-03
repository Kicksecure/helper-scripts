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

## Tests

Comprehensive tests + fuzzers for several helper-scripts tools are too
high-volume for human review and live in the AI-maintained dist-ai repo, not
here (https://github.com/org-ai-assisted/dist-ai). Run each against this
checkout:

    SANITIZE_STRING_BIN="$PWD/usr/bin/sanitize-string" sanitize-string-tests   # usr/share/sanitize-string-tests/
    STDISPLAY_REPO="$PWD" stcat-family-tests                                    # usr/share/stcat-family-tests/
    UNICODE_SHOW_REPO="$PWD" unicode-show-tests                                 # usr/share/unicode-show-tests/
    GREP_FIND_UNICODE_WRAPPER_REPO="$PWD" grep-find-unicode-wrapper-tests       # usr/share/grep-find-unicode-wrapper-tests/
    CHECK_REF_COMMITS_REPO="$PWD" check-ref-commits-for-unicode-tests           # usr/share/check-ref-commits-for-unicode-tests/
