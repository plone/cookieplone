"""Tests for cookieplone.config.schemas.repository."""

import json
from pathlib import Path

from cookieplone.config.schemas import validate_repository_config

RESOURCES = Path(__file__).parent.parent / "_resources" / "config"


def _minimal_repo():
    """Return a minimal valid repository config."""
    return {
        "version": "1.0",
        "title": "Test Templates",
        "groups": {
            "main": {
                "title": "Main",
                "description": "Main templates",
                "templates": ["project"],
                "hidden": False,
            },
        },
        "templates": {
            "project": {
                "path": "./templates/project",
                "title": "Project",
                "description": "A project template",
                "hidden": False,
            },
        },
    }


class TestValidateRepositoryConfig:
    """Tests for validate_repository_config."""

    def test_minimal_valid(self):
        valid, errors = validate_repository_config(_minimal_repo())
        assert valid is True
        assert errors == []

    def test_fixture_file(self):
        """Validate the full test fixture."""
        data = json.loads((RESOURCES / "cookieplone-config.json").read_text())
        valid, errors = validate_repository_config(data)
        assert valid is True, errors

    def test_with_description(self):
        data = _minimal_repo()
        data["description"] = "Templates for testing"
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_with_extends(self):
        data = _minimal_repo()
        data["extends"] = "gh:plone/cookieplone-templates"
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_with_empty_extends(self):
        data = _minimal_repo()
        data["extends"] = ""
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_with_config_versions(self):
        data = _minimal_repo()
        data["config"] = {"versions": {"gha_checkout": "v6"}}
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_with_config_renderer(self):
        data = _minimal_repo()
        data["config"] = {"renderer": "rich"}
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_with_config_versions_and_renderer(self):
        data = _minimal_repo()
        data["config"] = {
            "versions": {"gha_checkout": "v6"},
            "renderer": "stdlib",
        }
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_renderer_must_be_string(self):
        data = _minimal_repo()
        data["config"] = {"renderer": 42}
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_renderer_must_not_be_empty_string(self):
        data = _minimal_repo()
        data["config"] = {"renderer": ""}
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_multiple_groups(self):
        data = _minimal_repo()
        data["groups"]["addons"] = {
            "title": "Add-ons",
            "description": "Add-on templates",
            "templates": ["addon"],
            "hidden": False,
        }
        data["templates"]["addon"] = {
            "path": "./templates/addon",
            "title": "Add-on",
            "description": "An add-on template",
            "hidden": False,
        }
        valid, _errors = validate_repository_config(data)
        assert valid is True

    def test_hidden_group(self):
        data = _minimal_repo()
        data["groups"]["internal"] = {
            "title": "Internal",
            "description": "Internal templates",
            "templates": ["sub"],
            "hidden": True,
        }
        data["templates"]["sub"] = {
            "path": "./templates/sub",
            "title": "Sub",
            "description": "A sub-template",
            "hidden": True,
        }
        valid, _errors = validate_repository_config(data)
        assert valid is True

    # -- Structural validation errors --

    def test_missing_version(self):
        data = _minimal_repo()
        del data["version"]
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_wrong_version(self):
        data = _minimal_repo()
        data["version"] = "2.0"
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_missing_title(self):
        data = _minimal_repo()
        del data["title"]
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_missing_templates(self):
        data = _minimal_repo()
        del data["templates"]
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_empty_templates(self):
        data = _minimal_repo()
        data["templates"] = {}
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_template_missing_path(self):
        data = _minimal_repo()
        del data["templates"]["project"]["path"]
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_template_missing_title(self):
        data = _minimal_repo()
        del data["templates"]["project"]["title"]
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_template_extra_key(self):
        data = _minimal_repo()
        data["templates"]["project"]["unknown"] = "value"
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_group_missing_title(self):
        data = _minimal_repo()
        del data["groups"]["main"]["title"]
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_group_empty_templates(self):
        data = _minimal_repo()
        data["groups"]["main"]["templates"] = []
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_extra_top_level_key(self):
        data = _minimal_repo()
        data["unknown"] = "value"
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_extra_config_key(self):
        data = _minimal_repo()
        data["config"] = {"unknown": "value"}
        valid, _errors = validate_repository_config(data)
        assert valid is False

    def test_empty_dict(self):
        valid, _errors = validate_repository_config({})
        assert valid is False

    # -- Cross-referential validation errors --

    def test_group_references_unknown_template(self):
        data = _minimal_repo()
        data["groups"]["main"]["templates"].append("nonexistent")
        valid, errors = validate_repository_config(data)
        assert valid is False
        assert any("nonexistent" in e for e in errors)

    def test_template_in_multiple_groups(self):
        data = _minimal_repo()
        data["groups"]["other"] = {
            "title": "Other",
            "description": "Other templates",
            "templates": ["project"],
            "hidden": False,
        }
        valid, errors = validate_repository_config(data)
        assert valid is False
        assert any("appears in both" in e for e in errors)

    def test_template_not_in_any_group(self):
        data = _minimal_repo()
        data["templates"]["orphan"] = {
            "path": "./templates/orphan",
            "title": "Orphan",
            "description": "Orphan template",
            "hidden": False,
        }
        valid, errors = validate_repository_config(data)
        assert valid is False
        assert any("orphan" in e for e in errors)

    def test_no_groups_all_templates_ungrouped(self):
        data = _minimal_repo()
        del data["groups"]
        valid, errors = validate_repository_config(data)
        assert valid is False
        assert any("not assigned to any group" in e for e in errors)
