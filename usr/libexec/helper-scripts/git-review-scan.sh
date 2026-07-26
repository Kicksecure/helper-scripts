#!/bin/bash

## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## Shared content-hardening library for the safe git review tools. Sourced by
## git-review-driver.sh (external-diff mode) AND by the difftool/mergetool
## wrappers (git-review-difftool, git-review-mergetool). Holds the primitives
## that MUST stay identical across every review contract: Unicode/Trojan-Source
## surfacing, the fail-closed fatal handler, and a single-file content scan
## (Unicode + over-long line + binary) shared by the wrappers.
##
## The caller MUST set 'review_tool' (name used in messages) before sourcing.
##
## style-ok: no-strict (sourced-only; the caller sets strict-mode / errexit).

# shellcheck source=./wc-test.sh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/wc-test.sh
# shellcheck source=./has.sh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/has.sh
# shellcheck source=./log_run_die.sh
source "${HELPER_SCRIPTS_PATH:-}"/usr/libexec/helper-scripts/log_run_die.sh

has unicode-show
has stcat
has mktemp
has safe-rm

if [ -z "${review_tool:-}" ]; then
  die 2 "git-review-scan.sh: caller must set 'review_tool'"
fi

## Check for Unicode in a specified file. Makes unicode-show's return value
## public for other functions to inspect. Warns if Unicode is found, errors
## out or sets the fatal-finding flag if unicode-show reports a critical error
## or non-UTF data.
##
## unicode-show exits 0 on success when no Unicode is found, 1 on success when
## Unicode is found, 2 on errors including text decode errors. We
## intentionally suppress "missing newline at end" findings because symlink
## target placeholders in Git lack a trailing newline by design.
git_review_unicode_rc=0
git_review_unicode_scan() {
  local target label report

  target="$1"
  label="$2"
  git_review_unicode_rc=0
  report="$(UNICODE_SHOW_ALLOW_MISSING_FINAL_NEWLINE=1 NO_COLOR=1 unicode-show "${target}" 2>&1)" \
    || git_review_unicode_rc="$?"
  if [ "${git_review_unicode_rc}" != 0 ]; then
    log warn "'${label}' suspicious/undecodable Unicode (unicode-show rc='${git_review_unicode_rc}'):"
    printf '%s\n' "${report}" | stcat >&2 || true
    if [ "${git_review_unicode_rc}" -ge 2 ]; then
      git_review_handle_unicode_show_fatal
    fi
  fi
}

## Scan a path (not file content) for suspicious/undecodable bytes and for
## tab/newline forgery. Sets git_review_path_rc to unicode-show's exit code (0
## clean, 1 suspicious, >=2 undecodable) so the caller can decide whether a
## fatal path routes through git_review_handle_unicode_show_fatal. A trailing
## newline is appended before unicode-show, so no
## UNICODE_SHOW_ALLOW_MISSING_FINAL_NEWLINE.
git_review_path_rc=0
git_review_scan_path() {
  local path path_q report

  path="$1"
  path_q="$2"
  git_review_path_rc=0
  report="$(printf '%s\n' "${path}" | NO_COLOR=1 unicode-show 2>&1)" || git_review_path_rc="$?"
  if [ "${git_review_path_rc}" != 0 ]; then
    log warn "path '${path_q}' has suspicious/undecodable bytes (unicode-show rc='${git_review_path_rc}'):"
    printf '%s\n' "${report}" | stcat >&2 || true
  fi
  ## Tab / newline are the ONE gap unicode-show cannot cover: it treats them as
  ## benign content whitespace, yet in a PATH they are anomalous and can forge
  ## diff-output lines.
  case "${path}" in
    *$'\t'* | *$'\n'*)
      log warn "path '${path_q}' contains a tab or newline byte - anomalous in a filename; it can forge diff-output lines."
      ;;
  esac
}

## Fail-closed gate for a .gitattributes change (it can remap diff behavior to
## HIDE other files' content from the diff, and a legitimate change is rare in
## review). Args: $1 = a context label, $2... = the 'git ... --name-only -z'
## command to run. GIT_REVIEW_ALLOW_GITATTRIBUTES=1 downgrades the failure to a
## warning.
##
## Detection reads '-z' (RAW, NUL-separated names) into an array and matches with
## 'case', NOT a grep over 'git diff --name-only' text, and NOT a
## 'printf | grep --quiet' pipe:
##   - Without -z, git QUOTES any path with a non-ASCII byte or a control char
##     (core.quotePath), e.g. a '.gitattributes' in a non-ASCII-named directory
##     prints double-quoted -- an anchored '.gitattributes$' match then MISSES it
##     while git still applies the file.
##   - 'printf | grep --quiet' exits on the first match (and '.gitattributes'
##     sorts near the top), so printf takes SIGPIPE which pipefail turns into a
##     masked match.
## A temp file (not a '<(...)' process substitution) is used so git's exit code
## is captured -- a git failure is 'uncheckable' and also fails closed.
git_review_gitattributes_gate() {
  local context names_rc hit name names_file
  local -a name_list

  context="$1"
  shift

  names_file="$(mktemp git-review-attrnames.XXXXXX)"
  names_rc=0
  "$@" > "${names_file}" 2>/dev/null || names_rc=$?
  hit='false'
  if [ "${names_rc}" != 0 ]; then
    hit="uncheckable (git rc '${names_rc}')"
  else
    name_list=()
    readarray -d '' name_list < "${names_file}"
    for name in "${name_list[@]}"; do
      case "${name}" in
        .gitattributes | */.gitattributes)
          hit='changed'
          break
          ;;
      esac
    done
  fi
  safe-rm --force -- "${names_file}"

  if [ "${hit}" = 'false' ]; then
    return 0
  fi
  if [ -n "${GIT_REVIEW_ALLOW_GITATTRIBUTES:-}" ]; then
    log warn ".gitattributes ${hit} in ${context}, can hide OTHER files' contents. Tolerated via GIT_REVIEW_ALLOW_GITATTRIBUTES. Review it first."
    return 0
  fi
  log error ".gitattributes ${hit} in ${context}, can hide OTHER files' contents. Failing closed."
  log notice "Hint: legitimate .gitattributes changes are rare; set GIT_REVIEW_ALLOW_GITATTRIBUTES=1 to review anyway."
  exit 1
}

## Interactively ask the operator whether to continue a review despite content
## a scan flagged. Requires that the review tool be able to handle text that
## triggers unicode-show fatal errors. The prompt itself (log question +
## /dev/tty read + [y/N] default-no) is prompt_yes_no_tty (log_run_die.sh).
## Consent is not cached; a file that trips the scan more than once has multiple
## issues, each of which should require separate acknowledgement.
##
## Returns: 0 = proceed (operator said yes); 1 = operator explicitly declined;
## 2 = could not ask (not a terminal-safe reviewer, or no usable controlling
## terminal).
git_review_prompt_continue() {
  local prompt_rc

  if [ "${git_review_display_fatal_content:-}" != 'true' ]; then
    return 2
  fi
  ## The tty probe + /dev/tty read + [y/N] default-no live in prompt_yes_no_tty
  ## (log_run_die.sh); its 0/1/2 return maps exactly onto ours. This wrapper adds
  ## only the terminal-safe-reviewer gate above.
  prompt_rc=0
  prompt_yes_no_tty "Continue the review anyway?" || prompt_rc="$?"
  return "${prompt_rc}"
}

git_review_handle_unicode_show_fatal() {
  ## Usually we want to simply exit non-zero here. However, the user might
  ## want to try to review a diff even if a UTF-8 decode error was thrown
  ## by unicode-show. Because files that trigger such errors are liable to
  ## exploit vulnerabilities in diff viewers, we only allow this if:
  ##
  ## * the diff viewer plugin has declared itself able to display possibly
  ##   malicious files safely, AND one of the following is true:
  ##   * The user explicitly confirms they want to continue the review, OR
  ##   * the user has set GIT_REVIEW_UNICODE_NONFATAL=1 in the environment,
  ##     AND git_review_fatal_flag_file points to a file where we can store
  ##     info about problematic files (this happens only when one of the
  ##     wrappers is called directly, see git-review-driver.sh).
  ##
  ## At time of writing, the only diff viewer plugin that fulfills the
  ## first requirement is git-diff-review, which pipes all output through
  ## stcat.
  ##
  ## Note that a fatal error may have occurred for reasons other than a failed
  ## UTF-8 decode attempt (e.g., unreadable files will trigger this as well),
  ## so even if all of these conditions hold, the diff may still fail.

  if [ -n "${GIT_REVIEW_UNICODE_NONFATAL:-}" ] \
    && [ -n "${git_review_fatal_flag_file:-}" ] \
    && [ "${git_review_display_fatal_content:-}" = 'true' ]; then
    ## Record the finding for the end-of-run failure. A write error must NOT
    ## be swallowed - dropping it would let a fatal finding pass as clean.
    if ! printf '%s' '.' > "${git_review_fatal_flag_file}"; then
      die 1 "'${diff_path_q:-(file)}' triggered a fatal error in unicode-show and its finding could not be recorded. Failing closed."
    fi
    return 0
  fi

  log error "'${diff_path_q:-(file)}' triggered a fatal error in unicode-show."
  if git_review_prompt_continue; then
    return 0
  fi

  log error 'Failing closed.'
  log notice "Hint: To review this diff despite the errors, run via the git-diff-review wrapper and answer the continue prompt, or set GIT_REVIEW_UNICODE_NONFATAL=1. GUI wrappers (git-meld, git-kdiff3) cannot review this diff."
  exit 1
}

## Trap target: remove the fatal flag file if it exists.
# shellcheck disable=SC2317
git_review_cleanup() {
  if [ -n "${git_review_fatal_flag_file:-}" ]; then
    safe-rm --force -- "${git_review_fatal_flag_file}"
  fi
}

## Check a specified file for Unicode and overly long lines, and warn if
## either is found. Also checks a file for binary content and sets
## git_review_is_binary to 'true' if detected. That global is an OUT-param read
## by the callers (git-review-driver.sh / -difftool / -mergetool), not within
## this file, so shellcheck cannot see the use.
# shellcheck disable=SC2034
git_review_scan_content() {
  local target label longest nul_rc

  target="$1"
  label="$2"

  git_review_unicode_scan "${target}" "${label}"

  ## Over-long lines can truncate/hang a viewer (a place to bury a change).
  ## Do not silence errors from wc, if it fails something is very wrong.
  longest="$(wc --max-line-length < "${target}")"
  if [ "${longest}" -gt 5000 ]; then
    log warn "'${label}' has a '${longest}'-char line; a viewer may truncate/hang."
  fi

  ## A binary blob would render as noise in a text/GUI viewer. '--text' is
  ## required: without it GNU grep's binary-file heuristic will report no NUL
  ## matches, causing us to misclassify a file as text.
  ##
  ## grep rc: 0 == NUL found, 1 == none, >= 2 == grep error. We treat grep
  ## errors as binary so a possibly-binary blob is never opened as text.
  ##
  ## Do NOT use the --quiet option of grep, this causes errors to result in an
  ## exit code of 0!
  git_review_is_binary='false'
  if [ "${target}" != /dev/null ]; then
    nul_rc=0
    LC_ALL=C grep --text --perl-regexp '\x00' -- "${target}" >/dev/null 2>&1 || nul_rc=$?
    if [ "${nul_rc}" = 0 ]; then
      git_review_is_binary='true'
    elif [ "${nul_rc}" -ge 2 ]; then
      git_review_is_binary='true'
      log warn "NUL check for '${label}' errored (grep rc='${nul_rc}'); treating as binary."
    fi
  fi
}
