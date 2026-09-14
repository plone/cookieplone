#!/usr/bin/env bash
# Generate the example repository in docs/_examples/template-features/ and compare
# the output with the expected files shown in the documentation.
#
# The how-to guides and concept pages about validators, computed fields, filters,
# and hidden templates include their samples from that repository, so this check
# exercises what readers copy:
#
#   features         validators, computed and constant fields, filters enabled in
#                    config.extensions, a computed directory name
#   internal         a hidden template in a hidden group, run by its ID without --all
#   rejected-answer  a custom validator rejecting a value with --no-input
#
# The only addition to the documented commands is --config-file, which keeps
# Cookieplone's clone and replay directories out of the home directory.
#
# Usage, from the repository root:
#
#     bash docs/_checks/check_template_features.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXAMPLE="$ROOT/docs/_examples/template-features"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Run cookieplone in $WORK/$1 with the remaining arguments.
# Sets RUN_STATUS and RUN_LOG.
run_cookieplone() {
    local name="$1"
    shift
    local base="$WORK/$name"
    mkdir -p "$base"
    cp -R "$EXAMPLE/my-templates" "$base/my-templates"
    printf 'cookiecutters_dir: %s\nreplay_dir: %s\n' \
        "$base/cookiecutters" "$base/replay" > "$base/config.yaml"
    RUN_LOG="$base/run.log"
    RUN_STATUS=0
    (cd "$base" && COOKIEPLONE_REPOSITORY=./my-templates \
        uv run --project "$ROOT" cookieplone "$@" \
        --config-file "$base/config.yaml" > "$RUN_LOG" 2>&1) || RUN_STATUS=$?
}

# Generate a template and compare the project directory with expected/$project.
check_generated() {
    local name="$1" project="$2"
    shift 2
    run_cookieplone "$name" "$@"
    local base="$WORK/$name"
    if [ "$RUN_STATUS" -ne 0 ]; then
        echo "[$name] cookieplone failed:"
        tail -20 "$RUN_LOG"
        return 1
    fi

    local status=0
    local expected_files actual_files
    expected_files="$( (cd "$EXAMPLE/expected/$project" && find . -type f; echo ./.cookieplone.json) | LC_ALL=C sort)"
    actual_files="$(cd "$base/$project" && find . -type f | LC_ALL=C sort)"
    if [ "$expected_files" != "$actual_files" ]; then
        echo "[$name] unexpected files in $project:"
        diff <(echo "$expected_files") <(echo "$actual_files") || true
        status=1
    fi
    while IFS= read -r expected; do
        local relative="${expected#"$EXAMPLE/expected/"}"
        if ! diff -u "$expected" "$base/$relative"; then
            status=1
        fi
    done < <(find "$EXAMPLE/expected/$project" -type f | LC_ALL=C sort)
    if [ "$status" -eq 0 ]; then
        echo "[$name] generated output matches the documentation."
    fi
    return "$status"
}

# Run a template with a value its validator rejects, and expect the message.
check_rejected() {
    local name="$1" message="$2"
    shift 2
    run_cookieplone "$name" "$@"
    # Rich wraps long lines, so compare with whitespace collapsed.
    if [ "$RUN_STATUS" -eq 0 ]; then
        echo "[$name] cookieplone accepted a value the validator should reject."
        return 1
    fi
    if ! tr -s ' \n' ' ' < "$RUN_LOG" | grep -qF "$message"; then
        echo "[$name] the error does not contain: $message"
        tail -20 "$RUN_LOG"
        return 1
    fi
    echo "[$name] the validator rejected the value with the documented message."
}

overall=0
check_generated features example-addon features --no-input || overall=1
check_generated internal internal-tool internal --no-input || overall=1
check_rejected rejected-answer "Use hyphens instead of spaces." \
    features "project_slug=example addon" --no-input || overall=1
exit "$overall"
