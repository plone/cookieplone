"""Tests for cookieplone.config.v1."""

from typing import Any

from cookieplone.config.v1 import parse_v1
from cookieplone.config.v2 import ParsedConfig


def test_returns_parsed_config():
    """parse_v1 returns a ParsedConfig."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "description": "A description",
        }
    }
    result = parse_v1(context)
    assert isinstance(result, ParsedConfig)


def test_result_has_version_2():
    """parse_v1 converts to v2 format with version key."""
    context = {
        "cookiecutter": {
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    assert result.schema.get("version") == "2.0"


def test_result_has_properties():
    """parse_v1 output has a properties key."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "description": "A description",
        }
    }
    result = parse_v1(context)
    assert "properties" in result.schema


def test_string_field_conversion():
    """String fields are converted to v2 string properties."""
    context = {
        "cookiecutter": {
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    prop = result.schema["properties"]["title"]
    assert prop["type"] == "string"
    assert prop["default"] == "My Project"


def test_computed_field_conversion():
    """Fields prefixed with __ are converted to computed format."""
    context = {
        "cookiecutter": {
            "__folder_name": "{{ cookiecutter.title | slugify }}",
        }
    }
    result = parse_v1(context)
    prop = result.schema["properties"]["__folder_name"]
    assert prop["format"] == "computed"


def test_constant_field_conversion():
    """Fields with _ prefix are extracted to config, not properties."""
    context = {
        "cookiecutter": {
            "_copy_without_render": ["*.png"],
        }
    }
    result = parse_v1(context)
    assert "_copy_without_render" not in result.schema.get("properties", {})
    assert result.no_render == ["*.png"]


def test_extensions_extracted_to_config():
    """_extensions is extracted to ParsedConfig.extensions."""
    context = {
        "cookiecutter": {
            "_extensions": ["cookieplone.filters.latest_plone"],
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    assert "_extensions" not in result.schema.get("properties", {})
    assert result.extensions == ["cookieplone.filters.latest_plone"]


def test_choice_field_default():
    """List fields get the first item as default."""
    context = {
        "cookiecutter": {
            "license": ["MIT", "GPL-2.0", "BSD-3-Clause"],
        }
    }
    result = parse_v1(context)
    prop = result.schema["properties"]["license"]
    assert prop["default"] == "MIT"


def test_choice_field_with_prompts():
    """List fields with __prompts__ produce oneOf choices."""
    context = {
        "cookiecutter": {
            "license": ["MIT", "GPL-2.0", "BSD-3-Clause"],
            "__prompts__": {
                "license": {
                    "__prompt__": "Choose a license",
                    "MIT": "MIT License",
                    "GPL-2.0": "GNU GPL v2",
                    "BSD-3-Clause": "BSD 3-Clause",
                },
            },
        }
    }
    result = parse_v1(context)
    prop = result.schema["properties"]["license"]
    assert "oneOf" in prop
    assert len(prop["oneOf"]) == 3
    assert prop["oneOf"][0]["const"] == "MIT"
    assert prop["oneOf"][0]["title"] == "MIT License"
    assert prop["default"] == "MIT"


def test_prompts_become_titles():
    """__prompts__ values become the title of the corresponding property."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "__prompts__": {
                "title": "Enter project title",
            },
        }
    }
    result = parse_v1(context)
    assert result.schema["properties"]["title"]["title"] == "Enter project title"


def test_prompts_not_in_properties():
    """__prompts__ itself is not included in properties."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "__prompts__": {
                "title": "Enter project title",
            },
        }
    }
    result = parse_v1(context)
    assert "__prompts__" not in result.schema["properties"]


def test_validators_applied():
    """__validators__ values become the validator of the corresponding property."""
    context = {
        "cookiecutter": {
            "hostname": "example.com",
            "__validators__": {
                "hostname": "cookieplone.validators.hostname",
            },
        }
    }
    result = parse_v1(context)
    assert (
        result.schema["properties"]["hostname"]["validator"]
        == "cookieplone.validators.hostname"
    )


def test_validators_not_in_properties():
    """__validators__ itself is not included in properties."""
    context = {
        "cookiecutter": {
            "hostname": "example.com",
            "__validators__": {
                "hostname": "cookieplone.validators.hostname",
            },
        }
    }
    result = parse_v1(context)
    assert "__validators__" not in result.schema["properties"]


def test_extracts_from_cookiecutter_key():
    """parse_v1 extracts data from the 'cookiecutter' key."""
    context = {
        "cookiecutter": {
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    assert "title" in result.schema["properties"]


def test_works_without_cookiecutter_key():
    """parse_v1 works when data is passed directly (no 'cookiecutter' wrapper)."""
    context: dict[str, Any] = {
        "title": "My Project",
    }
    result = parse_v1(context)
    assert "title" in result.schema["properties"]


def test_integer_field_conversion():
    """Integer fields are converted to v2 integer properties."""
    context = {
        "cookiecutter": {
            "port": 8080,
        }
    }
    result = parse_v1(context)
    prop = result.schema["properties"]["port"]
    assert prop["type"] == "integer"
    assert prop["default"] == 8080


def test_boolean_field_conversion():
    """Boolean fields are handled (stored as strings or kept as-is)."""
    context = {
        "cookiecutter": {
            "has_volto": True,
        }
    }
    result = parse_v1(context)
    assert "has_volto" in result.schema["properties"]


def test_subtemplates_extracted():
    """__cookieplone_subtemplates are extracted as structured objects."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "__cookieplone_subtemplates": [
                ["sub/backend", "Backend", "1"],
                ["sub/frontend", "Frontend", "{{ cookiecutter.has_frontend }}"],
            ],
        }
    }
    result = parse_v1(context)
    assert "__cookieplone_subtemplates" not in result.schema.get("properties", {})
    assert len(result.subtemplates) == 2
    assert result.subtemplates[0] == {
        "id": "sub/backend",
        "title": "Backend",
        "enabled": "1",
    }
    assert result.subtemplates[1] == {
        "id": "sub/frontend",
        "title": "Frontend",
        "enabled": "{{ cookiecutter.has_frontend }}",
    }


def test_template_id_extracted():
    """__cookieplone_template is extracted as template_id."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "__cookieplone_template": "project",
        }
    }
    result = parse_v1(context)
    assert "__cookieplone_template" not in result.schema.get("properties", {})
    assert result.template_id == "project"
