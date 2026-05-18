"""Tests for cookieplone.config.merge."""

from cookieplone.config.merge import ORIGINS_KEY
from cookieplone.config.merge import merge_repo_configs
from cookieplone.config.merge import normalize_extends
from cookieplone.exceptions import InvalidConfiguration
from pathlib import Path

import pytest


UPSTREAM_DIR = Path("upstream")
DOWNSTREAM_DIR = Path("downstream")


def _base_config(**overrides):
    data = {
        "version": "1.0",
        "title": "Upstream",
        "description": "Upstream templates",
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
    data.update(overrides)
    return data


def _merge(upstream, downstream):
    return merge_repo_configs(
        upstream,
        downstream,
        upstream_repo_dir=UPSTREAM_DIR,
        downstream_repo_dir=DOWNSTREAM_DIR,
    )


class TestNormalizeExtends:
    def test_none(self):
        assert normalize_extends(None) is None

    def test_empty_string(self):
        assert normalize_extends("") is None

    def test_string_form(self):
        assert normalize_extends("gh:plone/cookieplone-templates") == {
            "url": "gh:plone/cookieplone-templates",
            "tag": None,
        }

    def test_object_form_without_tag(self):
        assert normalize_extends({"url": "gh:plone/foo"}) == {
            "url": "gh:plone/foo",
            "tag": None,
        }

    def test_object_form_with_tag(self):
        assert normalize_extends({"url": "gh:plone/foo", "tag": "2.1.0"}) == {
            "url": "gh:plone/foo",
            "tag": "2.1.0",
        }

    def test_object_missing_url(self):
        with pytest.raises(InvalidConfiguration, match="must be a string or an object"):
            normalize_extends({"tag": "2.1.0"})

    def test_other_type_raises(self):
        with pytest.raises(InvalidConfiguration):
            normalize_extends(42)


class TestMergeRepoConfigs:
    def test_pure_inheritance(self):
        upstream = _base_config()
        downstream = {"version": "1.0", "title": "Downstream"}
        merged = _merge(upstream, downstream)

        assert merged["title"] == "Downstream"
        assert merged["templates"] == upstream["templates"]
        assert merged["groups"] == upstream["groups"]
        assert merged[ORIGINS_KEY] == {"project": str(UPSTREAM_DIR)}

    def test_downstream_wins_title_and_description(self):
        upstream = _base_config()
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "description": "Downstream desc",
        }
        merged = _merge(upstream, downstream)

        assert merged["title"] == "Downstream"
        assert merged["description"] == "Downstream desc"

    def test_downstream_description_falls_back_to_upstream(self):
        upstream = _base_config(description="Upstream desc")
        downstream = {"version": "1.0", "title": "Downstream"}
        merged = _merge(upstream, downstream)

        assert merged["description"] == "Upstream desc"

    def test_extends_stripped(self):
        upstream = _base_config()
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "extends": "gh:plone/upstream",
        }
        merged = _merge(upstream, downstream)

        assert "extends" not in merged

    def test_template_override(self):
        upstream = _base_config()
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "templates": {
                "project": {
                    "path": "./local/project",
                    "title": "Local Project",
                    "description": "Locally overridden",
                    "hidden": False,
                },
            },
        }
        merged = _merge(upstream, downstream)

        assert merged["templates"]["project"]["title"] == "Local Project"
        assert merged["templates"]["project"]["path"] == "./local/project"
        assert merged[ORIGINS_KEY]["project"] == str(DOWNSTREAM_DIR)

    def test_template_add_new(self):
        upstream = _base_config()
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "templates": {
                "addon": {
                    "path": "./templates/addon",
                    "title": "Addon",
                    "description": "A new addon",
                    "hidden": False,
                },
            },
        }
        merged = _merge(upstream, downstream)

        assert set(merged["templates"]) == {"project", "addon"}
        assert merged[ORIGINS_KEY]["project"] == str(UPSTREAM_DIR)
        assert merged[ORIGINS_KEY]["addon"] == str(DOWNSTREAM_DIR)

    def test_template_hide_via_redeclaration(self):
        """Redeclaring an upstream template with hidden=True hides it."""
        upstream = _base_config()
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "templates": {
                "project": {
                    "path": "./templates/project",
                    "title": "Project",
                    "description": "A project template",
                    "hidden": True,
                },
            },
        }
        merged = _merge(upstream, downstream)

        assert merged["templates"]["project"]["hidden"] is True
        assert merged[ORIGINS_KEY]["project"] == str(DOWNSTREAM_DIR)

    def test_group_replace_clobbers_templates_list(self):
        """Downstream group declarations replace the upstream `templates` list."""
        upstream = _base_config()
        upstream["groups"]["main"]["templates"] = ["project", "extra"]
        upstream["templates"]["extra"] = {
            "path": "./templates/extra",
            "title": "Extra",
            "description": "Extra",
            "hidden": False,
        }
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "groups": {
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["project"],
                    "hidden": False,
                },
            },
        }
        merged = _merge(upstream, downstream)

        assert merged["groups"]["main"]["templates"] == ["project"]

    def test_versions_shallow_merge(self):
        upstream = _base_config(config={"versions": {"gha": "v5", "node": "20"}})
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "config": {"versions": {"gha": "v6", "python": "3.12"}},
        }
        merged = _merge(upstream, downstream)

        assert merged["config"]["versions"] == {
            "gha": "v6",
            "node": "20",
            "python": "3.12",
        }

    def test_renderer_downstream_wins(self):
        upstream = _base_config(config={"renderer": "rich"})
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "config": {"renderer": "stdlib"},
        }
        merged = _merge(upstream, downstream)

        assert merged["config"]["renderer"] == "stdlib"

    def test_renderer_falls_back_to_upstream(self):
        upstream = _base_config(config={"renderer": "rich"})
        downstream = {"version": "1.0", "title": "Downstream"}
        merged = _merge(upstream, downstream)

        assert merged["config"]["renderer"] == "rich"

    def test_min_version_strictest_wins_downstream_higher(self):
        upstream = _base_config(config={"min_version": "2.0.0"})
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "config": {"min_version": "3.0.0"},
        }
        merged = _merge(upstream, downstream)

        assert merged["config"]["min_version"] == "3.0.0"

    def test_min_version_strictest_wins_upstream_higher(self):
        upstream = _base_config(config={"min_version": "3.0.0"})
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "config": {"min_version": "2.0.0"},
        }
        merged = _merge(upstream, downstream)

        assert merged["config"]["min_version"] == "3.0.0"

    def test_min_version_only_upstream(self):
        upstream = _base_config(config={"min_version": "2.0.0"})
        downstream = {"version": "1.0", "title": "Downstream"}
        merged = _merge(upstream, downstream)

        assert merged["config"]["min_version"] == "2.0.0"

    def test_min_version_only_downstream(self):
        upstream = _base_config()
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "config": {"min_version": "2.0.0"},
        }
        merged = _merge(upstream, downstream)

        assert merged["config"]["min_version"] == "2.0.0"

    def test_no_config_section_when_all_empty(self):
        upstream = _base_config()
        downstream = {"version": "1.0", "title": "Downstream"}
        merged = _merge(upstream, downstream)

        assert "config" not in merged

    def test_transitive_origins_preserved(self):
        """When upstream is itself a merged result, its origins survive."""
        c_dir = Path("repo_c")
        # Simulate result of B+C merge.
        upstream = {
            "version": "1.0",
            "title": "B",
            "templates": {
                "from_c": {
                    "path": "./templates/from_c",
                    "title": "From C",
                    "description": "Inherited from C",
                    "hidden": False,
                },
            },
            ORIGINS_KEY: {"from_c": str(c_dir)},
        }
        downstream = {"version": "1.0", "title": "A"}
        merged = _merge(upstream, downstream)

        # from_c must still point at C, not at upstream (B).
        assert merged[ORIGINS_KEY]["from_c"] == str(c_dir)
