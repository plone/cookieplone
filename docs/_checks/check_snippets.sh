#!/usr/bin/env bash
# Check the documentation against real generations:
#
#   1. the questions and trees of the template reference pages, against a fresh
#      inventory of cookieplone-templates at DOCS_TEMPLATES_REF (default: next);
#   2. the example repositories of the tutorials and how-to guides;
#   3. the tree in the "Create your first Plone project" tutorial.
#
# Usage, from anywhere:
#
#     docs/_checks/check_snippets.sh
#
# Needs network access, uv, Node.js, and git.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REF="${DOCS_TEMPLATES_REF:-next}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/cookieplone-snippets.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
cd "$ROOT"

git clone --quiet --depth 1 --branch "$REF" \
    https://github.com/plone/cookieplone-templates "$WORK/templates"

overall=0

echo "==> Template reference pages (cookieplone-templates $REF)"
if uv run python docs/_checks/inventory_templates.py \
    --templates-repo "$WORK/templates" --output "$WORK/inventory" \
    > "$WORK/inventory.log" 2>&1; then
    uv run python docs/_checks/template_pages.py --inventory "$WORK/inventory" || overall=1
else
    tail -30 "$WORK/inventory.log"
    overall=1
fi

echo "==> Example repositories"
bash docs/_checks/check_tutorial_template.sh || overall=1
bash docs/_checks/check_template_features.sh || overall=1

echo "==> First project tutorial"
COOKIEPLONE_REPOSITORY="$WORK/templates" bash docs/_checks/run_tutorial.sh || overall=1

exit "$overall"
