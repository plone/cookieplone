"""Tests for cookieplone.utils.subtemplates."""

from collections import OrderedDict
from cookieplone.config import CookieploneState
from cookieplone.settings import QUIET_MODE_VAR
from cookieplone.utils.subtemplates import _parse_subtemplate_entry
from cookieplone.utils.subtemplates import process_subtemplates
from cookieplone.utils.subtemplates import run_subtemplates
from unittest.mock import MagicMock
from unittest.mock import patch

import os
import pytest


@pytest.fixture
def make_state():
    """Create a CookieploneState with the given subtemplates."""

    def func(subtemplates: list[dict[str, str]]) -> CookieploneState:
        return CookieploneState(
            schema={"version": "2.0", "properties": {}},
            data={"cookiecutter": {}},
            subtemplates=subtemplates,
        )

    return func


class TestProcessSubtemplates:
    """Tests for process_subtemplates."""

    def test_empty_subtemplates(self, make_state):
        """Returns empty list when state has no subtemplates."""
        state = make_state([])
        assert process_subtemplates(state, {}) == []

    def test_none_subtemplates(self):
        """Returns empty list when subtemplates is None."""
        state = CookieploneState(
            schema={"version": "2.0", "properties": {}},
            data={"cookiecutter": {}},
        )
        assert process_subtemplates(state, {}) == []

    def test_static_enabled(self, make_state):
        """Static enabled values are passed through unchanged."""
        state = make_state([
            {"id": "sub/backend", "title": "Backend", "enabled": "1"},
            {"id": "sub/frontend", "title": "Frontend", "enabled": "0"},
        ])
        result = process_subtemplates(state, {})
        assert result == [
            ["sub/backend", "Backend", "1"],
            ["sub/frontend", "Frontend", "0"],
        ]

    def test_jinja_enabled_rendered(self, make_state):
        """Jinja2 expressions in enabled are rendered against the context."""
        state = make_state([
            {
                "id": "docs/starter",
                "title": "Documentation",
                "enabled": "{{ cookiecutter.initialize_docs }}",
            },
        ])
        data = {"initialize_docs": "1"}
        result = process_subtemplates(state, data)
        assert result == [["docs/starter", "Documentation", "1"]]

    def test_jinja_enabled_false(self, make_state):
        """Jinja2 expression resolves to the actual context value."""
        state = make_state([
            {
                "id": "sub/frontend",
                "title": "Frontend",
                "enabled": "{{ cookiecutter.has_frontend }}",
            },
        ])
        data = {"has_frontend": "0"}
        result = process_subtemplates(state, data)
        assert result == [["sub/frontend", "Frontend", "0"]]

    def test_mixed_static_and_jinja(self, make_state):
        """Mix of static and Jinja2 enabled values."""
        state = make_state([
            {"id": "sub/backend", "title": "Backend", "enabled": "1"},
            {
                "id": "sub/frontend",
                "title": "Frontend",
                "enabled": "{{ cookiecutter.has_frontend }}",
            },
            {"id": "sub/settings", "title": "Settings", "enabled": "1"},
        ])
        data = {"has_frontend": "1"}
        result = process_subtemplates(state, data)
        assert result == [
            ["sub/backend", "Backend", "1"],
            ["sub/frontend", "Frontend", "1"],
            ["sub/settings", "Settings", "1"],
        ]

    def test_preserves_order(self, make_state):
        """Output order matches input order."""
        state = make_state([
            {"id": "c", "title": "C", "enabled": "1"},
            {"id": "a", "title": "A", "enabled": "1"},
            {"id": "b", "title": "B", "enabled": "1"},
        ])
        result = process_subtemplates(state, {})
        assert [r[0] for r in result] == ["c", "a", "b"]


class TestParseSubtemplateEntry:
    """Tests for _parse_subtemplate_entry."""

    @pytest.mark.parametrize(
        "entry,expected",
        [
            (
                {"id": "sub/cache", "title": "Cache", "enabled": "1"},
                {
                    "id": "sub/cache",
                    "title": "Cache",
                    "enabled": "1",
                    "folder_name": "",
                },
            ),
            (
                {
                    "id": "sub/cache",
                    "title": "Cache",
                    "enabled": "1",
                    "folder_name": ".",
                },
                {
                    "id": "sub/cache",
                    "title": "Cache",
                    "enabled": "1",
                    "folder_name": ".",
                },
            ),
            (
                {
                    "id": "ci/gh_project",
                    "title": "GitHub CI",
                    "enabled": "1",
                    "folder_name": ".github",
                },
                {
                    "id": "ci/gh_project",
                    "title": "GitHub CI",
                    "enabled": "1",
                    "folder_name": ".github",
                },
            ),
        ],
        ids=["dict-no-folder", "dict-dot-folder", "dict-with-folder"],
    )
    def test_dict_format(self, entry, expected):
        """Dict entries are normalised correctly."""
        assert _parse_subtemplate_entry(entry) == expected

    @pytest.mark.parametrize(
        "entry,expected",
        [
            (
                ["sub/cache", "Cache", "1"],
                {
                    "id": "sub/cache",
                    "title": "Cache",
                    "enabled": "1",
                    "folder_name": "",
                },
            ),
            (
                ("sub/cache", "Cache", "0"),
                {
                    "id": "sub/cache",
                    "title": "Cache",
                    "enabled": "0",
                    "folder_name": "",
                },
            ),
            (
                ["ci/gh_project", "GitHub CI", "1", ".github"],
                {
                    "id": "ci/gh_project",
                    "title": "GitHub CI",
                    "enabled": "1",
                    "folder_name": ".github",
                },
            ),
        ],
        ids=["list-3-items", "tuple-3-items", "list-4-items-with-folder"],
    )
    def test_tuple_format(self, entry, expected):
        """Tuple/list entries are normalised correctly."""
        assert _parse_subtemplate_entry(entry) == expected

    @pytest.mark.parametrize(
        "entry",
        [
            ["only_two", "items"],
            "a string",
            42,
        ],
        ids=["short-list", "string", "int"],
    )
    def test_invalid_format_raises(self, entry):
        """Invalid entries raise ValueError."""
        with pytest.raises(ValueError, match="Unrecognized subtemplate entry format"):
            _parse_subtemplate_entry(entry)


class TestRunSubtemplates:
    """Tests for run_subtemplates."""

    @pytest.fixture
    def context(self):
        """A minimal cookiecutter context with subtemplates."""
        return OrderedDict({
            "title": "My Project",
            "__cookieplone_repository_path": "repo",
            "__cookieplone_subtemplates": [],
        })

    @pytest.fixture
    def output_dir(self, tmp_path):
        """A temporary output directory."""
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        return project_dir

    def test_empty_subtemplates(self, context, output_dir):
        """Returns empty dict when no subtemplates defined."""
        result = run_subtemplates(context, output_dir)
        assert result == {}

    def test_missing_subtemplates_key(self, output_dir):
        """Returns empty dict when __cookieplone_subtemplates is missing."""
        context = OrderedDict({"title": "My Project"})
        result = run_subtemplates(context, output_dir)
        assert result == {}

    @patch("cookieplone.utils.subtemplates.console_print")
    def test_disabled_subtemplate_skipped(self, mock_print, context, output_dir):
        """Disabled subtemplates are skipped with a log message."""
        context["__cookieplone_subtemplates"] = [
            {
                "id": "sub/cache",
                "title": "Cache structure",
                "enabled": "0",
                "folder_name": ".",
            },
        ]
        result = run_subtemplates(context, output_dir)
        assert result == {}
        mock_print.assert_called_once_with(" -> Ignoring (Cache structure)")

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_enabled_without_handler_calls_default(
        self, mock_print, mock_generate, context, output_dir
    ):
        """Enabled subtemplate without handler calls generate_subtemplate."""
        generated_path = output_dir / "backend"
        mock_generate.return_value = generated_path
        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/backend",
                "title": "Backend add-on",
                "enabled": "1",
                "folder_name": "backend",
            },
        ]
        result = run_subtemplates(context, output_dir)
        assert result == {"add-ons/backend": generated_path}
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["template_path"] == "templates/add-ons/backend"
        assert call_kwargs.kwargs["output_dir"] == output_dir
        assert call_kwargs.kwargs["folder_name"] == "backend"

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_dot_folder_name_merges_into_project(
        self, mock_print, mock_generate, context, output_dir
    ):
        """folder_name '.' generates into parent dir with project name."""
        generated_path = output_dir
        mock_generate.return_value = generated_path
        context["__cookieplone_subtemplates"] = [
            {
                "id": "sub/cache",
                "title": "Cache",
                "enabled": "1",
                "folder_name": ".",
            },
        ]
        result = run_subtemplates(context, output_dir)
        assert result == {"sub/cache": generated_path}
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["output_dir"] == output_dir.parent
        assert call_kwargs.kwargs["folder_name"] == output_dir.name

    @patch("cookieplone.utils.subtemplates.console_print")
    def test_handler_called_for_matching_id(self, mock_print, context, output_dir):
        """Custom handler is called when template_id matches."""
        handler = MagicMock(return_value=output_dir / "frontend")
        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/frontend",
                "title": "Frontend add-on",
                "enabled": "1",
                "folder_name": "frontend",
            },
        ]
        result = run_subtemplates(
            context, output_dir, handlers={"add-ons/frontend": handler}
        )
        assert result == {"add-ons/frontend": output_dir / "frontend"}
        handler.assert_called_once()
        # Handler receives a deep copy, not the original context
        call_args = handler.call_args[0]
        assert call_args[0] is not context
        assert call_args[0] == context
        assert call_args[1] == output_dir

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_mixed_handlers_and_defaults(
        self, mock_print, mock_generate, context, output_dir
    ):
        """Mix of custom handlers and default generation."""
        handler = MagicMock(return_value=output_dir / "frontend")
        mock_generate.return_value = output_dir / "backend"
        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/backend",
                "title": "Backend",
                "enabled": "1",
                "folder_name": "backend",
            },
            {
                "id": "add-ons/frontend",
                "title": "Frontend",
                "enabled": "1",
                "folder_name": "frontend",
            },
            {
                "id": "sub/cache",
                "title": "Cache",
                "enabled": "0",
                "folder_name": ".",
            },
        ]
        result = run_subtemplates(
            context, output_dir, handlers={"add-ons/frontend": handler}
        )
        assert "add-ons/backend" in result
        assert "add-ons/frontend" in result
        assert "sub/cache" not in result  # disabled
        mock_generate.assert_called_once()  # backend only
        handler.assert_called_once()  # frontend only

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_preserves_order(self, mock_print, mock_generate, context, output_dir):
        """Results preserve the order of subtemplates."""
        mock_generate.side_effect = [
            output_dir / "a",
            output_dir / "b",
            output_dir / "c",
        ]
        context["__cookieplone_subtemplates"] = [
            {"id": "z", "title": "Z", "enabled": "1", "folder_name": "a"},
            {"id": "m", "title": "M", "enabled": "1", "folder_name": "b"},
            {"id": "a", "title": "A", "enabled": "1", "folder_name": "c"},
        ]
        result = run_subtemplates(context, output_dir)
        assert list(result.keys()) == ["z", "m", "a"]

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_tuple_format_entries(self, mock_print, mock_generate, context, output_dir):
        """Legacy tuple format entries work correctly."""
        mock_generate.return_value = output_dir
        context["__cookieplone_subtemplates"] = [
            ["sub/cache", "Cache", "1"],
        ]
        result = run_subtemplates(context, output_dir)
        assert "sub/cache" in result
        # No folder_name in tuple → empty → falls back to output_dir.name
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["folder_name"] == output_dir.name

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_no_folder_name_uses_output_dir_name(
        self, mock_print, mock_generate, context, output_dir
    ):
        """Missing folder_name falls back to output_dir.name."""
        mock_generate.return_value = output_dir
        context["__cookieplone_subtemplates"] = [
            {"id": "sub/settings", "title": "Settings", "enabled": "1"},
        ]
        run_subtemplates(context, output_dir)
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["output_dir"] == output_dir
        assert call_kwargs.kwargs["folder_name"] == output_dir.name

    @patch("cookieplone.utils.subtemplates.console_print")
    def test_handler_dispatch_runs_in_quiet_mode(
        self, mock_print, context, output_dir, monkeypatch
    ):
        """Each handler is invoked with QUIET_MODE_VAR active."""
        monkeypatch.delenv(QUIET_MODE_VAR, raising=False)
        observed: list[bool] = []

        def spy_handler(_context, _output_dir):
            observed.append(os.environ.get(QUIET_MODE_VAR) == "1")
            return _output_dir / "generated"

        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/backend",
                "title": "Backend",
                "enabled": "1",
                "folder_name": "backend",
            },
            {
                "id": "add-ons/frontend",
                "title": "Frontend",
                "enabled": "1",
                "folder_name": "frontend",
            },
        ]
        run_subtemplates(
            context,
            output_dir,
            handlers={
                "add-ons/backend": spy_handler,
                "add-ons/frontend": spy_handler,
            },
        )
        assert observed == [True, True]

    @patch("cookieplone.utils.subtemplates.console_print")
    def test_quiet_mode_disabled_after_completion(
        self, mock_print, context, output_dir, monkeypatch
    ):
        """Quiet mode is cleared after run_subtemplates returns."""
        monkeypatch.delenv(QUIET_MODE_VAR, raising=False)
        handler = MagicMock(return_value=output_dir / "generated")
        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/backend",
                "title": "Backend",
                "enabled": "1",
                "folder_name": "backend",
            },
        ]
        run_subtemplates(context, output_dir, handlers={"add-ons/backend": handler})
        assert QUIET_MODE_VAR not in os.environ

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_forwards_global_versions(
        self, mock_print, mock_generate, context, output_dir
    ):
        """global_versions is forwarded to generate_subtemplate calls."""
        mock_generate.return_value = output_dir / "backend"
        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/backend",
                "title": "Backend",
                "enabled": "1",
                "folder_name": "backend",
            },
        ]
        versions = {"plone.api": "2.1.0", "plone.restapi": "9.0.0"}
        run_subtemplates(context, output_dir, global_versions=versions)
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["global_versions"] == versions

    @patch("cookieplone.generator.generate_subtemplate")
    @patch("cookieplone.utils.subtemplates.console_print")
    def test_global_versions_defaults_to_none(
        self, mock_print, mock_generate, context, output_dir
    ):
        """global_versions defaults to None when not provided."""
        mock_generate.return_value = output_dir / "backend"
        context["__cookieplone_subtemplates"] = [
            {
                "id": "add-ons/backend",
                "title": "Backend",
                "enabled": "1",
                "folder_name": "backend",
            },
        ]
        run_subtemplates(context, output_dir)
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["global_versions"] is None
