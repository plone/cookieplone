#!/usr/bin/env bash
# Generate the project of the "Create your first Plone project" tutorial without
# questions, from the answers file the tutorial shows, and check that the tree in
# the tutorial matches the generated project.
#
# Run it from anywhere:
#
#   docs/_checks/run_tutorial.sh           # check the tutorial
#   docs/_checks/run_tutorial.sh --write   # update the tree in the tutorial
#
# The project template needs uv, Node.js, and git, and looks up the latest Plone
# and Volto releases online. Set COOKIEPLONE_REPOSITORY to use a local checkout of
# cookieplone-templates instead of downloading it.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PAGE="$ROOT/docs/src/tutorials/create-your-first-plone-project.md"
ANSWERS="$ROOT/docs/_examples/first-project/answers.json"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/cookieplone-tutorial.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

printf 'cookiecutters_dir: %s\nreplay_dir: %s\n' "$WORK/cookiecutters" "$WORK/replay" \
    > "$WORK/config.yaml"
mkdir "$WORK/output"
cd "$WORK"
if ! uv run --project "$ROOT" cookieplone --answers-file "$ANSWERS" --no-input \
    --config-file "$WORK/config.yaml" --output-dir "$WORK/output" \
    > "$WORK/cookieplone.log" 2>&1; then
    tail -30 "$WORK/cookieplone.log"
    exit 1
fi
uv run --project "$ROOT" python "$ROOT/docs/_checks/check_tree.py" \
    --dir "$WORK/output/my-plone-site" --page "$PAGE" --depth 1 "$@"
