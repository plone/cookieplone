"""Tests for go-back navigation and review-retry behaviour.

These tests exercise tui-forms' rendering fixtures to verify that:
- Going back preserves previously entered answers as defaults (issue #159).
- Computed fields are recalculated after the user changes answers
  on review retry (issue #160).
"""


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMA_WITH_COMPUTED = {
    "title": "Test Form",
    "description": "",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "title": "Project Title",
            "default": "My Project",
        },
        "project_slug": {
            "type": "string",
            "title": "Project Slug",
            "default": "{{ cookiecutter.title | lower | replace(' ', '-') }}",
        },
        "__folder_name": {
            "type": "string",
            "title": "Folder Name",
            "default": "{{ cookiecutter.project_slug }}",
            "format": "computed",
        },
    },
    "required": [],
}

SCHEMA_WITH_STATIC = {
    "title": "Test Form",
    "description": "",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "title": "Project Title",
            "default": "My Project",
        },
        "version": {
            "type": "string",
            "title": "Version",
            "default": "1.0.0",
        },
        "description": {
            "type": "string",
            "title": "Description",
            "default": "A project",
        },
    },
    "required": [],
}


# ---------------------------------------------------------------------------
# Issue #159 — go-back loses user-entered values
# ---------------------------------------------------------------------------


class TestGoBackPreservesAnswers:
    """When the user types '<' to go back, the previous answer should be
    offered as the default on re-ask, not the original schema default."""

    def test_go_back_shows_previous_answer_as_default(self, make_form, render_form):
        """After answering version='custom-version' and going back from
        description, pressing Enter on version should keep 'custom-version'."""
        frm = make_form(SCHEMA_WITH_STATIC, root_key="cookiecutter")
        # Flow: title, version=custom-version, go-back from description,
        # accept version default (Enter), answer description
        answers = render_form(
            frm,
            ["My Project", "custom-version", "<", "", "A project"],
        )
        assert answers["cookiecutter"]["version"] == "custom-version", (
            "Go-back lost the user's previous answer (issue #159)."
        )

    def test_go_back_preserves_computed_dependent_value(self, make_form, render_form):
        """When going back to a field whose default is a Jinja2 expression,
        the user's custom value should still be shown on re-ask."""
        frm = make_form(SCHEMA_WITH_COMPUTED, root_key="cookiecutter")
        # Flow: title, slug=custom-slug, go-back from end-of-form,
        # accept slug default (Enter)
        # Note: __folder_name is computed (hidden), so after project_slug
        # we've answered all visible questions. We go back to re-ask slug.
        answers = render_form(
            frm,
            ["Test One", "custom-slug", "<", ""],
        )
        assert answers["cookiecutter"]["project_slug"] == "custom-slug", (
            "Go-back lost the user's custom value for a computed-default field."
        )


# ---------------------------------------------------------------------------
# Issue #160 — computed fields stale after review retry
# ---------------------------------------------------------------------------


class TestReviewRetryRecomputesFields:
    """When the user declines confirmation and changes an answer that a
    computed field depends on, the computed field must be recalculated."""

    def test_computed_field_updated_after_slug_change(self, make_form, render_form):
        """If user changes project_slug on review retry, __folder_name must
        reflect the new slug, not the old one."""
        frm = make_form(SCHEMA_WITH_COMPUTED, root_key="cookiecutter")
        # Flow:
        #   Pass 1: title, slug-1, decline review ("n")
        #   Pass 2: title, slug-2, accept review ("y")
        answers = render_form(
            frm,
            ["My Project", "slug-1", "n", "My Project", "slug-2", "y"],
            confirm=True,
        )
        slug = answers["cookiecutter"]["project_slug"]
        folder_name = answers["cookiecutter"]["__folder_name"]
        assert slug == "slug-2", f"Expected project_slug='slug-2' but got '{slug}'"
        assert folder_name == "slug-2", (
            f"Expected __folder_name='slug-2' but got '{folder_name}'. "
            "Computed field was not recalculated after review retry (issue #160)."
        )
