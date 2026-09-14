"""Write and check the generated blocks of the template reference pages.

Each page ``docs/src/reference/templates/<id>.md`` documents one visible
template of ``cookieplone-templates``.  Two blocks of the page come from the
inventory built by ``inventory_templates.py``, never from memory:

- the questions table, between ``% questions:begin`` and ``% questions:end``;
- the generated tree, between ``% tree:begin`` and ``% tree:end``.

Everything outside the blocks is written by hand.

Check that every page matches the inventory (the default), or rewrite the
blocks with ``--write``.  Run it from the repository root::

    uv run python docs/_checks/template_pages.py
    uv run python docs/_checks/template_pages.py --write
"""

from cookieplone.settings import DEFAULT_VALIDATORS
from pathlib import Path
from typing import Any

import argparse
import difflib
import json
import re
import sys


# Formats that tui_forms never asks about.
HIDDEN_FORMATS = {"computed", "constant"}
# Formats for which tui_forms adds a validator when the field has none.
FORMAT_VALIDATORS = {"date", "date-time", "data-url", "email", "idn-email"}
# JSON Schema keywords that tui_forms enforces on top of any validator.
KEYWORD_CONSTRAINTS = ("minLength", "maxLength", "pattern", "minimum", "maximum")
BLOCKS = ("questions", "tree")
BLOCK_RE = re.compile(
    r"(?P<begin>^% (?P<name>[a-z]+):begin\n).*?(?P<end>^% (?P=name):end\n)",
    re.DOTALL | re.MULTILINE,
)
NONE = "—"


def insert_conditional(
    questions: list[dict[str, Any]],
    properties: dict[str, dict[str, Any]],
    item: dict[str, Any],
) -> None:
    """Insert the questions of one ``allOf`` item, as ``tui_forms`` does.

    :param questions: The questions built so far; changed in place.
    :param properties: Top-level properties, with default validators assigned.
    :param item: An ``allOf`` entry with ``if`` and ``then`` blocks.
    """
    condition = [
        (key, value["const"])
        for key, value in item.get("if", {}).get("properties", {}).items()
        if "const" in value
    ]
    gating_key = condition[0][0] if condition else ""
    insert_at = len(questions)
    for index, question in enumerate(questions):
        if question["key"] == gating_key:
            insert_at = index + 1
    while insert_at < len(questions) and questions[insert_at]["condition"]:
        insert_at += 1
    for key, prop in item["then"].get("properties", {}).items():
        merged = {**properties.get(key, {}), **prop}
        for index, question in enumerate(questions):
            if question["key"] == key and question["condition"] is None:
                questions.pop(index)
                if index < insert_at:
                    insert_at -= 1
                break
        questions.insert(
            insert_at, {"key": key, "prop": merged, "condition": condition or None}
        )
        insert_at += 1


def visible_questions(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the questions a user is asked, in the order they are asked.

    Cookieplone first assigns ``DEFAULT_VALIDATORS`` to top-level fields without
    a validator.  ``tui_forms`` then builds one question per property, and
    inserts the properties of each ``allOf`` ``then`` block, merged over the
    top-level definition, right after the question that gates them.  A
    conditional property replaces the unconditional question of the same key.
    Computed and constant questions are dropped at the end.

    :param schema: The ``schema`` object of a template's ``cookieplone.json``.
    :returns: Dicts with ``key``, ``prop`` (the effective property definition),
        and ``condition`` (a list of ``(key, value)`` pairs, or ``None``).
    """
    properties = {key: dict(prop) for key, prop in schema["properties"].items()}
    for key, validator in DEFAULT_VALIDATORS.items():
        if key in properties and not properties[key].get("validator"):
            properties[key]["validator"] = validator

    questions: list[dict[str, Any]] = [
        {"key": key, "prop": prop, "condition": None}
        for key, prop in properties.items()
    ]
    for item in schema.get("allOf", []):
        if item.get("then"):
            insert_conditional(questions, properties, item)
    return [
        question
        for question in questions
        if question["prop"].get("format", "") not in HIDDEN_FORMATS
    ]


def code(value: Any) -> str:
    """Format *value* as inline code, as it appears in ``cookieplone.json``.

    :param value: A default or choice value.
    :returns: Inline code; strings appear without JSON quotes unless empty.
    """
    text = value if isinstance(value, str) and value else json.dumps(value)
    fence = "``" if "`" in text else "`"
    return f"{fence}{text}{fence}"


def question_cell(question: dict[str, Any]) -> str:
    """Return the question title, with the condition that gates it."""
    title = question["prop"].get("title", question["key"])
    if not question["condition"]:
        return title
    parts = " and ".join(
        f"`{key}` is {code(value)}" for key, value in question["condition"]
    )
    return f"{title} (asked only when {parts})"


def choices_cell(prop: dict[str, Any]) -> str:
    """Return the choices of a ``oneOf`` or ``enum`` field."""
    if one_of := prop.get("oneOf"):
        return ", ".join(f"{code(item['const'])} ({item['title']})" for item in one_of)
    if enum := prop.get("enum"):
        return ", ".join(code(item) for item in enum)
    return NONE


def validation_cell(prop: dict[str, Any]) -> str:
    """Return the checks that run on an answer to this field."""
    checks = []
    if validator := prop.get("validator"):
        checks.append(f"`{validator}`")
    elif prop.get("format") in FORMAT_VALIDATORS:
        checks.append(f"`{prop['format']}` format")
    checks.extend(
        f"`{keyword}: {json.dumps(prop[keyword])}`"
        for keyword in KEYWORD_CONSTRAINTS
        if keyword in prop
    )
    return ", ".join(checks) if checks else NONE


def render_questions(schema: dict[str, Any]) -> str:
    """Render the questions of *schema* as a MyST list table.

    Titles and choices are quoted from the template as written, so Vale is
    turned off around the table.
    """
    lines = [
        "<!-- vale off -->",
        "",
        ":::{list-table}",
        ":header-rows: 1",
        "",
        "* - Field",
        "  - Question",
        "  - Default",
        "  - Choices",
        "  - Validation",
    ]
    for question in visible_questions(schema):
        prop = question["prop"]
        default = code(prop["default"]) if "default" in prop else NONE
        lines.extend([
            f"* - `{question['key']}`",
            f"  - {question_cell(question)}",
            f"  - {default}",
            f"  - {choices_cell(prop)}",
            f"  - {validation_cell(prop)}",
        ])
    lines.extend([":::", "", "<!-- vale on -->"])
    return "\n".join(lines) + "\n"


def render_tree(tree: str) -> str:
    """Render a generated tree listing as a fenced text block."""
    return f"```text\n{tree}```\n"


def update_page(text: str, blocks: dict[str, str]) -> tuple[str, set[str]]:
    """Replace the content of each generated block in a page.

    :param text: The page source.
    :param blocks: New content by block name.
    :returns: The updated source and the names of the blocks found.
    """
    found: set[str] = set()

    def replace(match: re.Match) -> str:
        name = match.group("name")
        if name not in blocks:
            return match.group(0)
        found.add(name)
        return f"{match.group('begin')}\n{blocks[name]}\n{match.group('end')}"

    return BLOCK_RE.sub(replace, text), found


def main() -> int:
    """Check or write every template page and return the process exit code."""
    parser = argparse.ArgumentParser(description="Check the template pages.")
    parser.add_argument(
        "--inventory", type=Path, default=Path("docs/_templates-inventory")
    )
    parser.add_argument(
        "--pages", type=Path, default=Path("docs/src/reference/templates")
    )
    parser.add_argument(
        "--write", action="store_true", help="Rewrite the generated blocks."
    )
    args = parser.parse_args()

    index = json.loads((args.inventory / "index.json").read_text())
    failures = 0
    for template_id in sorted(key for key in index if not key.startswith("_")):
        page = args.pages / f"{template_id}.md"
        if not page.exists():
            print(f"{page}: missing")
            failures += 1
            continue
        schema = json.loads(
            (args.inventory / f"{template_id}.schema.json").read_text()
        )["schema"]
        tree = (args.inventory / f"{template_id}.tree.txt").read_text()
        current = page.read_text()
        expected, found = update_page(
            current, {"questions": render_questions(schema), "tree": render_tree(tree)}
        )
        if missing := [name for name in BLOCKS if name not in found]:
            print(f"{page}: no {', '.join(missing)} block")
            failures += 1
            continue
        if expected == current:
            print(f"{page}: ok")
        elif args.write:
            page.write_text(expected)
            print(f"{page}: updated")
        else:
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=f"{page} (page)",
                tofile=f"{page} (inventory)",
            )
            sys.stdout.writelines(diff)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
