"""Tests for cookieplone.config.schemas.template."""

from cookieplone.config.schemas import validate_cookieplone_config

import pytest


def _minimal_v2():
    """Return a minimal valid v2 config."""
    return {
        "schema": {
            "version": "2.0",
            "properties": {
                "title": {
                    "type": "string",
                    "default": "My Project",
                },
            },
        },
    }


class TestValidateCookieploneConfig:
    """Tests for validate_cookieplone_config."""

    def test_minimal_valid(self):
        assert validate_cookieplone_config(_minimal_v2()) is True

    def test_with_id(self):
        data = _minimal_v2()
        data["id"] = "project"
        assert validate_cookieplone_config(data) is True

    def test_with_config_extensions(self):
        data = _minimal_v2()
        data["config"] = {"extensions": ["cookieplone.filters.latest_plone"]}
        assert validate_cookieplone_config(data) is True

    def test_with_config_no_render(self):
        data = _minimal_v2()
        data["config"] = {"no_render": ["*.png", "devops/etc"]}
        assert validate_cookieplone_config(data) is True

    def test_with_config_versions(self):
        data = _minimal_v2()
        data["config"] = {"versions": {"gha_checkout": "v6", "plone": "6.1"}}
        assert validate_cookieplone_config(data) is True

    def test_with_config_subtemplates(self):
        data = _minimal_v2()
        data["config"] = {
            "subtemplates": [
                {"id": "sub/backend", "title": "Backend", "enabled": "1"},
            ],
        }
        assert validate_cookieplone_config(data) is True

    def test_full_config(self):
        data = {
            "id": "project",
            "schema": {
                "title": "Cookieplone Project",
                "description": "A Plone project",
                "version": "2.0",
                "properties": {
                    "title": {
                        "type": "string",
                        "title": "Project Title",
                        "default": "My Project",
                    },
                    "__folder_name": {
                        "type": "string",
                        "format": "computed",
                        "default": "{{ cookiecutter.title | slugify }}",
                    },
                },
            },
            "config": {
                "extensions": ["cookieplone.filters.latest_plone"],
                "no_render": ["*.png"],
                "versions": {"gha_checkout": "v6"},
                "subtemplates": [
                    {"id": "sub/backend", "title": "Backend", "enabled": "1"},
                ],
            },
        }
        assert validate_cookieplone_config(data) is True

    def test_missing_schema(self):
        assert validate_cookieplone_config({"id": "test"}) is False

    def test_missing_version(self):
        data = {"schema": {"properties": {}}}
        assert validate_cookieplone_config(data) is False

    def test_wrong_version(self):
        data = {"schema": {"version": "1.0", "properties": {}}}
        assert validate_cookieplone_config(data) is False

    def test_missing_properties(self):
        data = {"schema": {"version": "2.0"}}
        assert validate_cookieplone_config(data) is False

    def test_extra_top_level_key(self):
        data = _minimal_v2()
        data["unknown_key"] = "value"
        assert validate_cookieplone_config(data) is False

    def test_extra_config_key(self):
        data = _minimal_v2()
        data["config"] = {"unknown": "value"}
        assert validate_cookieplone_config(data) is False

    def test_subtemplate_missing_id(self):
        data = _minimal_v2()
        data["config"] = {
            "subtemplates": [{"title": "Backend", "enabled": "1"}],
        }
        assert validate_cookieplone_config(data) is False

    def test_empty_dict(self):
        assert validate_cookieplone_config({}) is False

    @pytest.mark.parametrize(
        "property_def",
        [
            {"type": "string", "default": "value"},
            {"type": "integer", "default": 42},
            {"type": "boolean", "default": True},
            {"type": "string", "default": "x", "format": "computed"},
            {"type": "string", "default": "x", "validator": "mod.func"},
            {
                "type": "string",
                "default": "MIT",
                "oneOf": [
                    {"const": "MIT", "title": "MIT License"},
                    {"const": "GPL", "title": "GPL"},
                ],
            },
        ],
    )
    def test_valid_property_types(self, property_def):
        data = {
            "schema": {
                "version": "2.0",
                "properties": {"field": property_def},
            },
        }
        assert validate_cookieplone_config(data) is True
