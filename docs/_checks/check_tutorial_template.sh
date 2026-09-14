#!/usr/bin/env bash
# Generate the example repository of the "Create a template" tutorial and compare
# the rendered files with the expected output the tutorial shows.
#
# The tutorial includes its code samples from docs/_examples/create-a-template/,
# so this check exercises exactly what readers copy. It runs the tutorial's
# command from the directory that contains my-template/, with a relative
# COOKIEPLONE_REPOSITORY, twice: from a plain directory, as the tutorial does,
# and from a git repository with one commit, which the tutorial also states works.
#
# The only addition to the tutorial's command is --config-file, which keeps
# Cookieplone's clone and replay directories out of the home directory.
#
# Usage, from the repository root:
#
#     bash docs/_checks/check_tutorial_template.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXAMPLE="$ROOT/docs/_examples/create-a-template"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Generate the example in $WORK/$1 and compare it with the expected files.
run_scenario() {
    local name="$1"
    local base="$WORK/$name"
    mkdir -p "$base"
    cp -R "$EXAMPLE/my-template" "$base/my-template"
    if [ "$name" = "git-repository" ]; then
        git -C "$base/my-template" init --quiet
        git -C "$base/my-template" add .
        git -C "$base/my-template" -c user.name=docs -c user.email=docs@example.com \
            commit --quiet -m "Example template"
    fi
    printf 'cookiecutters_dir: %s\nreplay_dir: %s\n' \
        "$base/cookiecutters" "$base/replay" > "$base/config.yaml"

    (cd "$base" && COOKIEPLONE_REPOSITORY=./my-template \
        uv run --project "$ROOT" cookieplone myproject --no-input \
        --config-file "$base/config.yaml" > "$base/run.log" 2>&1) || {
        echo "[$name] cookieplone failed:"
        tail -20 "$base/run.log"
        return 1
    }

    local status=0
    # The file list shown in the tutorial's "Inspect the output" step.
    local files
    files="$(cd "$base/my-project" && find . -type f | LC_ALL=C sort)"
    if [ "$files" != "$(printf './.cookieplone.json\n./README.md\n./pyproject.toml')" ]; then
        echo "[$name] unexpected files in my-project:"
        echo "$files"
        status=1
    fi
    while IFS= read -r expected; do
        local relative="${expected#"$EXAMPLE/expected/"}"
        if ! diff -u "$expected" "$base/$relative"; then
            status=1
        fi
    done < <(find "$EXAMPLE/expected" -type f | sort)
    if [ "$status" -eq 0 ]; then
        echo "[$name] generated output matches the tutorial."
    fi
    return "$status"
}

overall=0
run_scenario plain-directory || overall=1
run_scenario git-repository || overall=1
exit "$overall"
