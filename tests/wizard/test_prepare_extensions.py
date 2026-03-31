"""Tests for _prepare_extensions."""

from cookieplone.settings import DEFAULT_EXTENSIONS
from cookieplone.wizard import _prepare_extensions


def test_includes_defaults():
    """Default extensions are always included."""
    result = _prepare_extensions([])
    for ext in DEFAULT_EXTENSIONS:
        assert ext in result


def test_includes_custom():
    """Custom extensions are included in the result."""
    custom = ["my.custom.Extension"]
    result = _prepare_extensions(custom)
    assert "my.custom.Extension" in result


def test_no_duplicates():
    """Duplicate extensions are deduplicated."""
    custom = [DEFAULT_EXTENSIONS[0]]
    result = _prepare_extensions(custom)
    assert result.count(DEFAULT_EXTENSIONS[0]) == 1


def test_merges_defaults_and_custom():
    """Result contains both default and custom extensions."""
    custom = ["my.Extension1", "my.Extension2"]
    result = _prepare_extensions(custom)
    assert len(result) >= len(DEFAULT_EXTENSIONS) + 2
