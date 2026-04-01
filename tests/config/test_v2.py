"""Tests for cookieplone.config.v2."""

from typing import Any

from cookieplone.config.v2 import ParsedConfig, parse_v2


def test_returns_parsed_config():
    """parse_v2 returns a ParsedConfig."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
    }
    result = parse_v2(context)
    assert isinstance(result, ParsedConfig)


def test_preserves_version():
    """parse_v2 preserves the version key in the schema."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
    }
    result = parse_v2(context)
    assert result.schema["version"] == "2.0"


def test_preserves_properties():
    """parse_v2 preserves the properties."""
    context: dict[str, Any] = {
        "schema": {
            "version": "2.0",
            "properties": {
                "title": {
                    "type": "string",
                    "default": "My Project",
                }
            },
        },
    }
    result = parse_v2(context)
    assert result.schema["properties"]["title"]["default"] == "My Project"


def test_preserves_computed_fields():
    """parse_v2 preserves computed fields."""
    context: dict[str, Any] = {
        "schema": {
            "version": "2.0",
            "properties": {
                "__folder_name": {
                    "type": "string",
                    "format": "computed",
                    "default": "{{ cookiecutter.title | slugify }}",
                }
            },
        },
    }
    result = parse_v2(context)
    prop = result.schema["properties"]["__folder_name"]
    assert prop["format"] == "computed"


def test_preserves_oneof_choices():
    """parse_v2 preserves oneOf choice fields."""
    context: dict[str, Any] = {
        "schema": {
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
        },
    }
    result = parse_v2(context)
    assert len(result.schema["properties"]["license"]["oneOf"]) == 2


def test_preserves_schema_title():
    """parse_v2 preserves title and description in the schema."""
    context: dict[str, Any] = {
        "schema": {
            "version": "2.0",
            "title": "My Form",
            "description": "A form description",
            "properties": {},
        },
    }
    result = parse_v2(context)
    assert result.schema["title"] == "My Form"
    assert result.schema["description"] == "A form description"


def test_empty_context():
    """parse_v2 handles an empty dict."""
    context: dict[str, Any] = {}
    result = parse_v2(context)
    assert result.schema == {}
    assert result.extensions == []
    assert result.no_render == []
    assert result.versions == {}
    assert result.subtemplates == []
    assert result.template_id == ""


def test_extracts_extensions():
    """parse_v2 extracts extensions from config."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
        "config": {
            "extensions": ["cookieplone.filters.latest_plone"],
        },
    }
    result = parse_v2(context)
    assert result.extensions == ["cookieplone.filters.latest_plone"]


def test_extracts_no_render():
    """parse_v2 extracts no_render from config."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
        "config": {
            "no_render": ["*.png", "devops/etc"],
        },
    }
    result = parse_v2(context)
    assert result.no_render == ["*.png", "devops/etc"]


def test_extracts_versions():
    """parse_v2 extracts versions from config."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
        "config": {
            "versions": {"gha_checkout": "v6", "plone": "6.1"},
        },
    }
    result = parse_v2(context)
    assert result.versions == {"gha_checkout": "v6", "plone": "6.1"}


def test_extracts_subtemplates():
    """parse_v2 extracts subtemplates from config."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
        "config": {
            "subtemplates": [
                {"id": "sub/backend", "title": "Backend", "enabled": "1"},
            ],
        },
    }
    result = parse_v2(context)
    assert len(result.subtemplates) == 1
    assert result.subtemplates[0] == {
        "id": "sub/backend",
        "title": "Backend",
        "enabled": "1",
    }


def test_extracts_template_id():
    """parse_v2 extracts the top-level id."""
    context: dict[str, Any] = {
        "id": "project",
        "schema": {"version": "2.0", "properties": {}},
    }
    result = parse_v2(context)
    assert result.template_id == "project"


def test_no_config_section():
    """parse_v2 works when there is no config section."""
    context: dict[str, Any] = {
        "schema": {"version": "2.0", "properties": {}},
    }
    result = parse_v2(context)
    assert result.extensions == []
    assert result.no_render == []
    assert result.versions == {}
    assert result.subtemplates == []
