"""Tests for cookieplone.utils.subtemplates."""

import pytest

from cookieplone.config import CookieploneState
from cookieplone.utils.subtemplates import process_subtemplates


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
