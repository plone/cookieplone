"""Tests for go-back navigation and review-retry behaviour.

These tests exercise tui-forms' BaseRenderer directly to verify that:
- Going back preserves previously entered answers as defaults (issue #159).
- Computed fields are recalculated after the user changes answers
  on review retry (issue #160).
"""

import contextlib
from unittest.mock import patch

import pytest
from tui_forms import create_form, get_renderer
from tui_forms.renderer.base import _GoBackRequest

# ---------------------------------------------------------------------------
# Helpers
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

    @pytest.mark.xfail(
        reason="tui-forms bug: unrecord() loses user answer (issue #159)"
    )
    def test_go_back_shows_previous_answer_as_default(self):
        """After answering q2='custom-version' and going back from q3,
        q2 should default to 'custom-version', not the schema default."""
        frm = create_form(SCHEMA_WITH_STATIC, root_key="cookiecutter")
        renderer = get_renderer("cookiecutter")(frm)

        # Flow: answer q1, answer q2='custom-version', on q3 go back,
        # q2 is re-asked — capture its default, then finish.
        call_count = 0
        observed_defaults = []

        original_dispatch = renderer._dispatch.__func__

        def patched_dispatch(self, question):
            nonlocal call_count
            call_count += 1
            # q1 (title): accept default
            if question.key == "title" and call_count == 1:
                return "My Project"
            # q2 (version) first time: answer 'custom-version'
            if question.key == "version" and call_count == 2:
                return "custom-version"
            # q3 (description): go back to re-ask q2
            if question.key == "description" and call_count == 3:
                raise _GoBackRequest()
            # q2 (version) second time: capture default
            if question.key == "version" and call_count == 4:
                default = question.default_value(
                    self._env, self._form.answers, self._form.root_key
                )
                observed_defaults.append(default)
                return default
            # q3 (description) second time: accept default
            if question.key == "description" and call_count == 5:
                return "A project"
            return original_dispatch(self, question)

        with patch.object(type(renderer), "_dispatch", patched_dispatch):
            renderer.render(confirm=False)

        # The key assertion: when q2 is re-asked after go-back,
        # the default should be the user's previous answer, not the schema default
        assert len(observed_defaults) == 1
        assert observed_defaults[0] == "custom-version", (
            f"Expected 'custom-version' but got '{observed_defaults[0]}'. "
            "Go-back lost the user's previous answer (issue #159)."
        )

    def test_go_back_preserves_computed_dependent_value(self):
        """When going back to a field whose default is a Jinja2 expression
        depending on an earlier answer, the user's custom value should still
        be shown, not the re-rendered default."""
        frm = create_form(SCHEMA_WITH_COMPUTED, root_key="cookiecutter")
        renderer = get_renderer("cookiecutter")(frm)

        call_count = 0
        observed_defaults = []

        def patched_dispatch(self, question):
            nonlocal call_count
            call_count += 1
            # q1 (title): answer 'Test One'
            if question.key == "title" and call_count == 1:
                return "Test One"
            # q2 (project_slug) first time: user enters 'custom-slug'
            if question.key == "project_slug" and call_count == 2:
                return "custom-slug"
            # Simulate: we are now past all questions, but let's go back to q2
            # q2 on re-ask: capture default
            if question.key == "project_slug" and call_count == 4:
                default = question.default_value(
                    self._env, self._form.answers, self._form.root_key
                )
                observed_defaults.append(default)
                return default
            # Trigger go-back at call_count == 3
            if call_count == 3:
                raise _GoBackRequest()
            raise _GoBackRequest()

        with (
            patch.object(type(renderer), "_dispatch", patched_dispatch),
            contextlib.suppress(_GoBackRequest),
        ):
            renderer.render(confirm=False)

        # The user entered 'custom-slug', not the Jinja-rendered 'test-one'
        if observed_defaults:
            assert observed_defaults[0] == "custom-slug", (
                f"Expected 'custom-slug' but got '{observed_defaults[0]}'. "
                "Go-back lost the user's custom value for a computed-default field."
            )


# ---------------------------------------------------------------------------
# Issue #160 — computed fields stale after review retry
# ---------------------------------------------------------------------------


class TestReviewRetryRecomputesFields:
    """When the user declines confirmation and changes an answer that a
    computed field depends on, the computed field must be recalculated."""

    @pytest.mark.xfail(
        reason="tui-forms bug: stale computed fields on retry (issue #160)"
    )
    def test_computed_field_updated_after_slug_change(self):
        """If user changes project_slug on review retry, __folder_name must
        reflect the new slug, not the old one."""
        frm = create_form(SCHEMA_WITH_COMPUTED, root_key="cookiecutter")
        renderer = get_renderer("cookiecutter")(frm)

        render_pass = 0

        def fake_ask_string(self, question, default, prefix):
            if question.key == "title":
                return "My Project"
            if question.key == "project_slug":
                # Pass 1 (render_pass==0): user enters 'slug-1'
                # Pass 2 (render_pass==1): user changes to 'slug-2'
                if render_pass == 0:
                    return "slug-1"
                return "slug-2"
            return str(default) if default else ""

        def fake_summary(self, user_answers):
            nonlocal render_pass
            render_pass += 1
            # First review: reject to trigger retry; second: accept
            return render_pass != 1

        with (
            patch.object(type(renderer), "_ask_string", fake_ask_string),
            patch.object(type(renderer), "render_summary", fake_summary),
        ):
            answers = renderer.render(confirm=True)

        slug = answers.get("cookiecutter", {}).get("project_slug")
        folder_name = answers.get("cookiecutter", {}).get("__folder_name")
        assert slug == "slug-2", f"Expected project_slug='slug-2' but got '{slug}'"
        assert folder_name == "slug-2", (
            f"Expected __folder_name='slug-2' but got '{folder_name}'. "
            "Computed field was not recalculated after review retry (issue #160)."
        )
