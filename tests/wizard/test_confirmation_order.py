"""Tests for confirmation-screen answer ordering (issue #202).

The confirmation screen shown after all answers are supplied is rendered by
tui-forms' ``render_summary``, which iterates ``form.user_answers.items()``.
The order the user sees is therefore exactly the iteration order of
``user_answers``.

These tests assert that ``user_answers`` preserves the order in which the
questions were declared in the schema. They fail while ``user_answers`` is
built by iterating an unordered set, and pass once insertion order is kept.
"""

# A schema with enough fields that an unordered iteration reliably diverges
# from the declared order (the probability of a set happening to iterate in
# declaration order across this many keys is negligible).
SCHEMA_ORDERED = {
    "title": "Test Form",
    "description": "",
    "type": "object",
    "properties": {
        "title": {"type": "string", "default": "My Project"},
        "description": {"type": "string", "default": "A project"},
        "author": {"type": "string", "default": "Jane Doe"},
        "email": {"type": "string", "default": "jane@example.com"},
        "python_package_name": {"type": "string", "default": "my.project"},
        "volto_addon_name": {"type": "string", "default": "volto-my-addon"},
        "license": {"type": "string", "default": "GPLv2"},
        "workflow": {"type": "string", "default": "default"},
    },
    "required": [],
}


class TestConfirmationScreenOrder:
    """The confirmation screen must list answers in the schema's question order."""

    def test_user_answers_preserve_question_order(self, make_form, render_form):
        """``form.user_answers`` (the data the confirmation screen iterates)
        must follow the order the questions were declared in the schema."""
        frm = make_form(SCHEMA_ORDERED, root_key="cookiecutter")
        expected = list(SCHEMA_ORDERED["properties"].keys())
        # Accept every default in order (empty input == accept default), which
        # records each key as user-provided.
        render_form(frm, [""] * len(expected))
        assert list(frm.user_answers.keys()) == expected, (
            "The confirmation screen does not preserve the form's question "
            "order (issue #202)."
        )
