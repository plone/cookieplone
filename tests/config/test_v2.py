"""Tests for cookieplone.config.v2."""

from typing import Any

from cookieplone.config.v2 import parse_v2


def test_returns_dict():
    """parse_v2 returns a dict."""
    context: dict[str, Any] = {"version": "2.0", "properties": {}}
    result = parse_v2(context)
    assert isinstance(result, dict)


def test_returns_same_object():
    """parse_v2 returns the exact same dict (pass-through)."""
    context: dict[str, Any] = {"version": "2.0", "properties": {}}
    result = parse_v2(context)
    assert result is context


def test_preserves_version():
    """parse_v2 preserves the version key."""
    context: dict[str, Any] = {"version": "2.0", "properties": {}}
    result = parse_v2(context)
    assert result["version"] == "2.0"


def test_preserves_properties():
    """parse_v2 preserves the properties."""
    context: dict[str, Any] = {
        "version": "2.0",
        "properties": {
            "title": {
                "type": "string",
                "default": "My Project",
            }
        },
    }
    result = parse_v2(context)
    assert result["properties"]["title"]["default"] == "My Project"


def test_preserves_computed_fields():
    """parse_v2 preserves computed fields."""
    context: dict[str, Any] = {
        "version": "2.0",
        "properties": {
            "__folder_name": {
                "type": "string",
                "format": "computed",
                "default": "{{ cookiecutter.title | slugify }}",
            }
        },
    }
    result = parse_v2(context)
    prop = result["properties"]["__folder_name"]
    assert prop["format"] == "computed"


def test_preserves_oneof_choices():
    """parse_v2 preserves oneOf choice fields."""
    context: dict[str, Any] = {
        "version": "2.0",
        "properties": {
            "license": {
                "type": "string",
                "oneOf": [
                    {"const": "MIT", "title": "MIT License"},
                    {"const": "GPL-2.0", "title": "GNU GPL v2"},
                ],
                "default": "MIT",
            }
        },
    }
    result = parse_v2(context)
    assert len(result["properties"]["license"]["oneOf"]) == 2


def test_preserves_extra_keys():
    """parse_v2 preserves any extra keys in the context."""
    context: dict[str, Any] = {
        "version": "2.0",
        "title": "My Form",
        "description": "A form description",
        "properties": {},
    }
    result = parse_v2(context)
    assert result["title"] == "My Form"
    assert result["description"] == "A form description"


def test_empty_context():
    """parse_v2 handles an empty dict."""
    context: dict[str, Any] = {}
    result = parse_v2(context)
    assert result == {}
