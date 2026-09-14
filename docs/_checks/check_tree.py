"""Check or update a generated file tree shown in a documentation page.

The page holds the tree between ``% tree:begin`` and ``% tree:end``, rendered
by ``render_tree`` from ``inventory_templates.py``.  Run it from the repository
root::

    uv run python docs/_checks/check_tree.py --dir <generated folder> \\
        --page docs/src/tutorials/create-your-first-plone-project.md --depth 1
"""

from pathlib import Path
from typing import Any

import argparse
import difflib
import importlib.util
import re
import sys


CHECKS = Path(__file__).resolve().parent
TREE_RE = re.compile(
    r"(?P<begin>^% tree:begin\n).*?(?P<end>^% tree:end\n)",
    re.DOTALL | re.MULTILINE,
)


def load_inventory() -> Any:
    """Import ``inventory_templates.py`` from this directory.

    :returns: The module.
    """
    spec = importlib.util.spec_from_file_location(
        "inventory_templates", CHECKS / "inventory_templates.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    """Check or update the tree block and return the process exit code."""
    parser = argparse.ArgumentParser(description="Check a tree in a page.")
    parser.add_argument("--dir", type=Path, required=True, help="Generated folder.")
    parser.add_argument("--page", type=Path, required=True, help="Page to check.")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--write", action="store_true", help="Update the page.")
    args = parser.parse_args()

    tree = load_inventory().render_tree(args.dir, args.depth)
    current = args.page.read_text()
    match = TREE_RE.search(current)
    if not match:
        print(f"{args.page}: no tree block")
        return 1
    block = f"{match.group('begin')}\n```text\n{tree}```\n\n{match.group('end')}"
    expected = current[: match.start()] + block + current[match.end() :]
    if expected == current:
        print(f"{args.page}: tree matches {args.dir.name}")
        return 0
    if args.write:
        args.page.write_text(expected)
        print(f"{args.page}: tree updated")
        return 0
    sys.stdout.writelines(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile=f"{args.page} (page)",
            tofile=f"{args.page} (generated)",
        )
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
