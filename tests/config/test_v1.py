"""Tests for cookieplone.config.v1."""

from typing import Any

from cookieplone.config.v1 import parse_v1


def test_returns_dict():
    """parse_v1 returns a dict."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "description": "A description",
        }
    }
    result = parse_v1(context)
    assert isinstance(result, dict)


def test_result_has_version_2():
    """parse_v1 converts to v2 format with version key."""
    context = {
        "cookiecutter": {
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    assert result.get("version") == "2.0"


def test_result_has_properties():
    """parse_v1 output has a properties key."""
    context = {
        "cookiecutter": {
            "title": "My Project",
            "description": "A description",
        }
    }
    result = parse_v1(context)
    assert "properties" in result


def test_string_field_conversion():
    """String fields are converted to v2 string properties."""
    context = {
        "cookiecutter": {
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    prop = result["properties"]["title"]
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
    prop = result["properties"]["__folder_name"]
    assert prop["format"] == "computed"


def test_constant_field_conversion():
    """Fields prefixed with _ (single underscore) are converted to constant format."""
    context = {
        "cookiecutter": {
            "_copy_without_render": [],
        }
    }
    result = parse_v1(context)
    prop = result["properties"]["_copy_without_render"]
    assert prop["format"] == "constant"


def test_choice_field_default():
    """List fields get the first item as default."""
    context = {
        "cookiecutter": {
            "license": ["MIT", "GPL-2.0", "BSD-3-Clause"],
        }
    }
    result = parse_v1(context)
    prop = result["properties"]["license"]
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
    prop = result["properties"]["license"]
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
    assert result["properties"]["title"]["title"] == "Enter project title"


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
    assert "__prompts__" not in result["properties"]


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
        result["properties"]["hostname"]["validator"]
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
    assert "__validators__" not in result["properties"]


def test_extracts_from_cookiecutter_key():
    """parse_v1 extracts data from the 'cookiecutter' key."""
    context = {
        "cookiecutter": {
            "title": "My Project",
        }
    }
    result = parse_v1(context)
    assert "title" in result["properties"]


def test_works_without_cookiecutter_key():
    """parse_v1 works when data is passed directly (no 'cookiecutter' wrapper)."""
    context: dict[str, Any] = {
        "title": "My Project",
    }
    result = parse_v1(context)
    assert "title" in result["properties"]


def test_integer_field_conversion():
    """Integer fields are converted to v2 integer properties."""
    context = {
        "cookiecutter": {
            "port": 8080,
        }
    }
    result = parse_v1(context)
    prop = result["properties"]["port"]
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
    assert "has_volto" in result["properties"]
