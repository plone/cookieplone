"""Integration tests for the ``extends`` mechanism through the public API.

These tests drive ``get_repository_config``, ``get_template_options`` and
``get_template_groups`` end-to-end against on-disk fake upstream/downstream
repositories.  They complement the lower-level merge and resolver tests
(``tests/config/test_merge.py``, ``tests/test_repository_extends_resolve.py``).
"""

from __future__ import annotations

from cookieplone import repository as r
from cookieplone.config.merge import ORIGINS_KEY
from cookieplone.exceptions import InvalidConfiguration
from cookieplone.exceptions import RepositoryException
from pathlib import Path
from typing import Any
from unittest.mock import patch

import json
import pytest


def _write_repo(
    path: Path,
    *,
    title: str,
    templates: dict[str, dict[str, Any]] | None = None,
    groups: dict[str, dict[str, Any]] | None = None,
    extends: Any = None,
    config: dict[str, Any] | None = None,
) -> Path:
    """Create a repo dir with a cookieplone-config.json on disk."""
    path.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {
        "version": "1.0",
        "title": title,
    }
    if extends is not None:
        data["extends"] = extends
    if templates is not None:
        data["templates"] = templates
    if groups is not None:
        data["groups"] = groups
    if config is not None:
        data["config"] = config
    (path / "cookieplone-config.json").write_text(json.dumps(data))
    return path


def _default_templates(prefix: str) -> dict[str, dict[str, Any]]:
    return {
        f"{prefix}_t1": {
            "path": f"./templates/{prefix}_t1",
            "title": f"{prefix} t1",
            "description": f"{prefix} template 1",
            "hidden": False,
        },
        f"{prefix}_t2": {
            "path": f"./templates/{prefix}_t2",
            "title": f"{prefix} t2",
            "description": f"{prefix} template 2",
            "hidden": False,
        },
    }


def _default_groups(prefix: str) -> dict[str, dict[str, Any]]:
    return {
        f"{prefix}_group": {
            "title": f"{prefix} Group",
            "description": f"{prefix} templates",
            "templates": [f"{prefix}_t1", f"{prefix}_t2"],
            "hidden": False,
        },
    }


@pytest.fixture
def patch_user_config(tmp_path: Path):
    """Patch get_user_config so clone_to_dir is rooted in tmp_path."""
    cookiecutters_dir = tmp_path / "_cookiecutters"
    cookiecutters_dir.mkdir(exist_ok=True)
    fake_config = {
        "cookiecutters_dir": str(cookiecutters_dir),
        "replay_dir": str(tmp_path / "_replay"),
        "abbreviations": {},
        "default_context": {},
    }
    with patch("cookieplone.repository.get_user_config", return_value=fake_config):
        yield fake_config


class TestGetRepositoryConfigWithExtends:
    """End-to-end tests for get_repository_config with `extends`."""

    def test_pure_extension_downstream(self, tmp_path: Path, patch_user_config):
        """A downstream with only `extends` inherits the full upstream."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
        )

        config = r.get_repository_config(downstream)

        assert set(config["templates"]) == {"up_t1", "up_t2"}
        assert "up_group" in config["groups"]
        assert config[ORIGINS_KEY]["up_t1"] == str(upstream.resolve())

    def test_override_existing_template(self, tmp_path: Path, patch_user_config):
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={
                "up_t1": {
                    "path": "./templates/local_t1",
                    "title": "Local override",
                    "description": "overridden",
                    "hidden": False,
                },
            },
        )

        config = r.get_repository_config(downstream)

        assert config["templates"]["up_t1"]["title"] == "Local override"
        assert config[ORIGINS_KEY]["up_t1"] == str(downstream.resolve())
        assert config[ORIGINS_KEY]["up_t2"] == str(upstream.resolve())

    def test_add_new_template(self, tmp_path: Path, patch_user_config):
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={
                "local_addon": {
                    "path": "./templates/local_addon",
                    "title": "Local Addon",
                    "description": "A new local addon",
                    "hidden": False,
                },
            },
            groups={
                "local_group": {
                    "title": "Local",
                    "description": "Local-only templates",
                    "templates": ["local_addon"],
                    "hidden": False,
                },
            },
        )

        config = r.get_repository_config(downstream)

        assert set(config["templates"]) == {"up_t1", "up_t2", "local_addon"}
        assert config[ORIGINS_KEY]["local_addon"] == str(downstream.resolve())

    def test_hide_upstream_via_redeclare(self, tmp_path: Path, patch_user_config):
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={
                "up_t1": {
                    "path": "./templates/up_t1",
                    "title": "up t1",
                    "description": "up template 1",
                    "hidden": True,
                },
            },
        )

        config = r.get_repository_config(downstream)
        assert config["templates"]["up_t1"]["hidden"] is True

        # get_template_options without --all should now exclude the redeclared
        # template that is hidden.
        visible = r.get_template_options(downstream, all_=False)
        assert "up_t1" not in visible
        assert "up_t2" in visible

    def test_versions_merge(self, tmp_path: Path, patch_user_config):
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
            config={"versions": {"gha": "v5", "node": "20"}},
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            config={"versions": {"gha": "v6", "python": "3.12"}},
        )

        config = r.get_repository_config(downstream)
        assert config["config"]["versions"] == {
            "gha": "v6",
            "node": "20",
            "python": "3.12",
        }

    def test_renderer_downstream_wins(self, tmp_path: Path, patch_user_config):
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
            config={"renderer": "rich"},
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            config={"renderer": "stdlib"},
        )

        config = r.get_repository_config(downstream)
        assert config["config"]["renderer"] == "stdlib"

    def test_min_version_strictest_wins(self, tmp_path: Path, patch_user_config):
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
            config={"min_version": "2.0.0"},
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            config={"min_version": "3.0.0"},
        )

        config = r.get_repository_config(downstream)
        assert config["config"]["min_version"] == "3.0.0"

    def test_transitive_chain(self, tmp_path: Path, patch_user_config):
        c = _write_repo(
            tmp_path / "c",
            title="C",
            templates=_default_templates("c"),
            groups=_default_groups("c"),
        )
        b = _write_repo(
            tmp_path / "b",
            title="B",
            extends=str(c),
            templates=_default_templates("b"),
            groups=_default_groups("b"),
        )
        a = _write_repo(
            tmp_path / "a",
            title="A",
            extends=str(b),
            templates=_default_templates("a"),
            groups=_default_groups("a"),
        )

        config = r.get_repository_config(a)
        assert {"a_t1", "a_t2", "b_t1", "b_t2", "c_t1", "c_t2"} <= set(
            config["templates"]
        )
        assert config[ORIGINS_KEY]["a_t1"] == str(a.resolve())
        assert config[ORIGINS_KEY]["b_t1"] == str(b.resolve())
        assert config[ORIGINS_KEY]["c_t1"] == str(c.resolve())

    def test_cycle_detection(self, tmp_path: Path, patch_user_config):
        a = tmp_path / "a"
        b = tmp_path / "b"
        _write_repo(
            a, title="A", templates=_default_templates("a"), groups=_default_groups("a")
        )
        _write_repo(
            b, title="B", templates=_default_templates("b"), groups=_default_groups("b")
        )
        _write_repo(
            a,
            title="A",
            templates=_default_templates("a"),
            groups=_default_groups("a"),
            extends=str(b),
        )
        _write_repo(
            b,
            title="B",
            templates=_default_templates("b"),
            groups=_default_groups("b"),
            extends=str(a),
        )

        with pytest.raises(InvalidConfiguration, match="Circular 'extends'"):
            r.get_repository_config(a)

    def test_unreachable_upstream(self, tmp_path: Path, patch_user_config):
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(tmp_path / "nonexistent"),
        )

        with pytest.raises(RepositoryException, match="Could not resolve 'extends'"):
            r.get_repository_config(downstream)

    def test_resolution_cached(self, tmp_path: Path, patch_user_config):
        """The merged config is cached: a second call returns the same dict."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
        )

        first = r.get_repository_config(downstream)
        second = r.get_repository_config(downstream)
        assert first is second


class TestGetTemplateOptionsWithExtends:
    """Template-listing helpers see the merged config + origin."""

    def test_origin_set_on_inherited_template(self, tmp_path: Path, patch_user_config):
        # Create the actual template directory so `path.resolve` lands on a
        # real location (the listing helper resolves the path but does not
        # require the target to exist as a config; we just want the test
        # not to be confused by missing directories on systems with strict
        # path resolution).
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "up_t1": {
                    "path": "./templates/up_t1",
                    "title": "up t1",
                    "description": "up template",
                    "hidden": False,
                },
            },
            groups={
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["up_t1"],
                    "hidden": False,
                },
            },
        )
        (upstream / "templates" / "up_t1").mkdir(parents=True)

        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
        )

        templates = r.get_template_options(downstream)
        assert "up_t1" in templates
        # The inherited template's origin must point at the upstream clone.
        assert templates["up_t1"].origin == upstream.resolve()
        # And its stored path is relative to that origin.
        assert templates["up_t1"].path == Path("templates/up_t1")

    def test_origin_for_local_template(self, tmp_path: Path, patch_user_config):
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            templates={
                "local": {
                    "path": "./templates/local",
                    "title": "local",
                    "description": "local",
                    "hidden": False,
                },
            },
            groups={
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["local"],
                    "hidden": False,
                },
            },
        )
        (downstream / "templates" / "local").mkdir(parents=True)

        templates = r.get_template_options(downstream)
        assert templates["local"].origin == downstream.resolve()


class TestPartialOverrides:
    """End-to-end coverage of per-field merge + template-file overlay."""

    def test_pure_hide_inherits_upstream_path(self, tmp_path: Path, patch_user_config):
        """Downstream `{hidden: true}` inherits path/title from upstream."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={"up_t1": {"hidden": True}},
        )

        config = r.get_repository_config(downstream)

        # Per-field merge: path/title/description fall back to upstream
        assert config["templates"]["up_t1"]["hidden"] is True
        assert config["templates"]["up_t1"]["path"] == "./templates/up_t1"
        # Origin stays upstream (downstream didn't supply path)
        assert config["_template_origins"]["up_t1"] == str(upstream.resolve())

    def test_partial_title_override(self, tmp_path: Path, patch_user_config):
        """Downstream supplies only title; description comes from upstream."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={"up_t1": {"title": "Renamed"}},
        )

        config = r.get_repository_config(downstream)
        assert config["templates"]["up_t1"]["title"] == "Renamed"
        assert config["templates"]["up_t1"]["description"] == "up template 1"

    def test_underlay_populated_when_downstream_supplies_path(
        self, tmp_path: Path, patch_user_config
    ):
        """When downstream supplies path, the parsed template carries an underlay."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "up_t1": {
                    "path": "./templates/up_t1",
                    "title": "up t1",
                    "description": "up template",
                    "hidden": False,
                },
            },
            groups={
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["up_t1"],
                    "hidden": False,
                },
            },
        )
        (upstream / "templates" / "up_t1").mkdir(parents=True)

        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={"up_t1": {"path": "./templates/up_t1"}},
        )
        (downstream / "templates" / "up_t1").mkdir(parents=True)

        templates = r.get_template_options(downstream)
        assert templates["up_t1"].origin == downstream.resolve()
        assert templates["up_t1"].underlay == [
            (upstream.resolve(), "./templates/up_t1"),
        ]

    def test_no_underlay_for_pure_metadata_redeclare(
        self, tmp_path: Path, patch_user_config
    ):
        """A pure metadata redeclare leaves the underlay empty (origin=upstream)."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        (upstream / "templates" / "up_t1").mkdir(parents=True)

        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={"up_t1": {"title": "Renamed"}},
        )

        templates = r.get_template_options(downstream)
        assert templates["up_t1"].origin == upstream.resolve()
        assert templates["up_t1"].underlay == []

    def test_overlay_root_repo_dir_points_at_downstream(
        self, tmp_path: Path, patch_user_config
    ):
        """For an overlay template, RepositoryInfo.root_repo_dir is the
        downstream (the origin root) — so __cookieplone_repository_path
        allows sibling-template lookups to find downstream overrides first,
        while still falling back to upstream layers via
        __cookieplone_upstream_repos."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "up_t1": {
                    "path": "./templates/up_t1",
                    "title": "up t1",
                    "description": "up template",
                    "hidden": False,
                },
            },
            groups={
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["up_t1"],
                    "hidden": False,
                },
            },
        )
        upstream_template = upstream / "templates" / "up_t1"
        upstream_template.mkdir(parents=True)
        (upstream_template / "cookieplone.json").write_text('{"upstream": true}')

        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={"up_t1": {"path": "./templates/up_t1"}},
        )
        ds_template = downstream / "templates" / "up_t1"
        ds_template.mkdir(parents=True)

        r.get_repository_config(downstream)
        chosen = r.get_template_options(downstream)["up_t1"]

        info = r.get_repository(
            repository=chosen.origin,
            template_name=chosen.name,
            template_path=str(chosen.path),
            accept_hooks=False,
            template_underlay=chosen.underlay,
        )

        try:
            assert info.root_repo_dir == downstream.resolve()
            # upstream_repos also tracked (excludes downstream).
            assert upstream.resolve() in info.upstream_repos
        finally:
            from cookieplone.utils import files as f_utils

            f_utils.remove_paths(info.cleanup_paths)

    def test_overlay_serves_upstream_cookieplone_json(
        self, tmp_path: Path, patch_user_config, monkeypatch
    ):
        """get_repository with underlay builds an overlay that serves the
        upstream cookieplone.json when downstream doesn't supply one."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "up_t1": {
                    "path": "./templates/up_t1",
                    "title": "up t1",
                    "description": "up template",
                    "hidden": False,
                },
            },
            groups={
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["up_t1"],
                    "hidden": False,
                },
            },
        )
        upstream_template = upstream / "templates" / "up_t1"
        upstream_template.mkdir(parents=True)
        (upstream_template / "cookieplone.json").write_text('{"upstream": true}')
        (upstream_template / "{{ cookiecutter.__folder_name }}").mkdir()
        (
            upstream_template / "{{ cookiecutter.__folder_name }}" / "README.md"
        ).write_text("upstream README")
        (
            upstream_template / "{{ cookiecutter.__folder_name }}" / "other.txt"
        ).write_text("untouched")

        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={"up_t1": {"path": "./templates/up_t1"}},
        )
        # Downstream local template: only the README, no cookieplone.json
        ds_template = downstream / "templates" / "up_t1"
        (ds_template / "{{ cookiecutter.__folder_name }}").mkdir(parents=True)
        (ds_template / "{{ cookiecutter.__folder_name }}" / "README.md").write_text(
            "downstream README"
        )

        # Populate the resolution cache the same way the CLI flow does
        r.get_repository_config(downstream)
        templates = r.get_template_options(downstream)
        chosen = templates["up_t1"]

        info = r.get_repository(
            repository=chosen.origin,
            template_name=chosen.name,
            template_path=str(chosen.path),
            accept_hooks=False,
            template_underlay=chosen.underlay,
        )

        overlay = info.base_repo_dir
        try:
            # cookieplone.json from upstream is now available in the overlay
            assert (overlay / "cookieplone.json").read_text() == '{"upstream": true}'
            # README from downstream
            assert (
                overlay / "{{ cookiecutter.__folder_name }}" / "README.md"
            ).read_text() == "downstream README"
            # other.txt from upstream, untouched
            assert (
                overlay / "{{ cookiecutter.__folder_name }}" / "other.txt"
            ).read_text() == "untouched"
            # Overlay dir is tracked for cleanup
            assert overlay in info.cleanup_paths
        finally:
            from cookieplone.utils import files as f_utils

            f_utils.remove_paths(info.cleanup_paths)


class TestMergedConfigValidation:
    """The merged result is re-validated; bad merges raise."""

    def test_subtemplate_override_priority(self, tmp_path: Path, patch_user_config):
        """Verify that a subtemplate override in downstream takes priority
        over the upstream version even when the parent template is an
        upstream overlay."""
        from cookieplone.utils import files as f_utils

        # Upstream repo with a subtemplate and a project template
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "project": {
                    "path": "./templates/project",
                    "title": "Project",
                    "description": "Project",
                },
                "sub/settings": {
                    "path": "./templates/sub/settings",
                    "title": "Settings",
                    "description": "Settings",
                },
            },
            groups={
                "main": {
                    "title": "Main",
                    "description": "Main",
                    "templates": ["project", "sub/settings"],
                }
            },
        )
        (upstream / "templates" / "project").mkdir(parents=True)
        sub_up = upstream / "templates" / "sub" / "settings"
        sub_up.mkdir(parents=True)
        (sub_up / "cookiecutter.json").write_text("{}")
        (sub_up / "README.md").write_text("upstream sub")

        # Downstream repo extends upstream and overrides BOTH the project
        # (as an overlay) and the subtemplate.
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={
                "project": {"path": "./templates/project"},
                "sub/settings": {"path": "./templates/sub/settings"},
            },
        )
        (downstream / "templates" / "project").mkdir(parents=True)
        sub_ds = downstream / "templates" / "sub" / "settings"
        sub_ds.mkdir(parents=True)
        (sub_ds / "cookiecutter.json").write_text("{}")
        (sub_ds / "README.md").write_text("downstream sub")

        # CLI flow: resolve config then list options
        r.get_repository_config(downstream)
        options = r.get_template_options(downstream)
        chosen = options["project"]

        info = r.get_repository(
            repository=chosen.origin,
            template_name=chosen.name,
            template_path=str(chosen.path),
            accept_hooks=False,
            template_underlay=chosen.underlay,
        )

        # Build context simulating what is passed to post-gen hook
        from cookieplone.generator.main import _annotate_data
        from cookieplone._types import RunConfig
        from cookieplone.config.state import CookieploneState

        context = {"cookiecutter": {}}
        state = CookieploneState(
            schema={"version": "2.0", "properties": {}},
            data=context,
            template_id="project",
        )
        run_config = RunConfig(
            output_dir=tmp_path / "output",
            no_input=True,
            accept_hooks=False,
            overwrite_if_exists=True,
            skip_if_file_exists=False,
            keep_project_on_failure=False,
        )

        _annotate_data(context["cookiecutter"], state, run_config, info)

        # Now simulate subtemplate resolution logic from f_utils.get_repository_root
        # as it would be called in a hook:
        # get_repository_root(context, "templates/sub/settings")
        try:
            resolved_sub_repo = f_utils.get_repository_root(
                context["cookiecutter"], "templates/sub/settings"
            )
            # It MUST point to downstream because downstream overrides it!
            assert resolved_sub_repo == downstream.resolve()
        finally:
            f_utils.remove_paths(info.cleanup_paths)

    def test_repository_overlay_full_integration(self, tmp_path: Path, patch_user_config):
        """Verify the full integration of template overlays and overrides."""
        # 1. Setup fake upstream
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream Templates",
            templates={
                "project": {
                    "path": "./templates/projects/main",
                    "title": "Base Project",
                    "description": "Base description",
                },
                "sub/settings": {
                    "path": "./templates/sub/settings",
                    "title": "Base Settings",
                    "description": "Base subtemplate",
                    "hidden": True,
                },
            },
            groups={
                "projects": {
                    "title": "Projects",
                    "description": "Generators",
                    "templates": ["project"],
                },
                "sub": {
                    "title": "Sub",
                    "description": "Subtemplates",
                    "templates": ["sub/settings"],
                },
            },
        )
        (upstream / "templates" / "projects" / "main").mkdir(parents=True)
        (upstream / "templates" / "sub" / "settings").mkdir(parents=True)

        # 2. Setup downstream extension
        downstream_config = {
            "version": "1.0",
            "title": "Downstream customization",
            "extends": str(upstream),
            "templates": {
                "project": {
                    "title": "Overridden Project",
                    "description": "Overridden description",
                    "path": "./templates/project",
                },
                "sub/settings": {
                    "path": "./templates/sub/settings",
                    "title": "Overridden Settings",
                    "description": "Overridden subtemplate",
                    "hidden": True,
                },
            },
        }
        downstream = tmp_path / "downstream"
        downstream.mkdir()
        (downstream / "cookieplone-config.json").write_text(
            json.dumps(downstream_config)
        )
        (downstream / "templates" / "project").mkdir(parents=True)
        (downstream / "templates" / "sub" / "settings").mkdir(parents=True)

        # 3. Resolve and verify config merging
        config = r.get_repository_config(downstream)

        # Assert per-field merge
        assert config["templates"]["project"]["title"] == "Overridden Project"
        assert config["templates"]["project"]["path"] == "./templates/project"

        # Assert layers are correct
        layers = config["_template_layers"]
        assert len(layers["project"]) == 2
        assert layers["project"][0] == [
            str(upstream.resolve()),
            "./templates/projects/main",
        ]
        assert layers["project"][1] == [str(downstream.resolve()), "./templates/project"]

        # Assert groups are preserved from upstream
        assert "projects" in config["groups"]
        assert "project" in config["groups"]["projects"]["templates"]

        # 4. Verify RepositoryInfo resolution logic
        templates = r.get_template_options(downstream)
        chosen = templates["project"]

        info = r.get_repository(
            repository=chosen.origin,
            template_name=chosen.name,
            template_path=str(chosen.path),
            accept_hooks=False,
            template_underlay=chosen.underlay,
        )

        try:
            # root_repo_dir must be downstream to find local overrides first
            assert info.root_repo_dir == downstream.resolve()
            # Upstream must be in the fallback list
            assert upstream.resolve() in info.upstream_repos
        finally:
            from cookieplone.utils import files as f_utils

            f_utils.remove_paths(info.cleanup_paths)

    def test_subtemplate_upstream_sharing_and_cleanup(
        self, tmp_path: Path, patch_user_config
    ):
        """Verify that subtemplates do not delete shared upstream clones."""
        from cookieplone.utils import files as f_utils

        # 1. Setup upstream with a subtemplate
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "sub/s1": {
                    "path": "./templates/sub/s1",
                    "title": "S1",
                    "description": "S1",
                }
            },
            groups={
                "sub": {
                    "title": "Sub",
                    "description": "Subtemplates",
                    "templates": ["sub/s1"],
                }
            },
        )
        (upstream / "templates" / "sub" / "s1").mkdir(parents=True)
        (upstream / "templates" / "sub" / "s1" / "cookiecutter.json").write_text("{}")

        # 2. Setup downstream
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
        )

        # 3. Simulate a subtemplate run that receives already-resolved upstreams
        # (mirroring what happens in a hook process)
        upstream_repos = [upstream.resolve()]

        info = r.get_repository(
            repository=str(downstream),
            template_name="sub/s1",
            template_path="templates/sub/s1",
            upstream_repos=upstream_repos,
        )

        # 4. CRUCIAL: upstream repositories MUST NOT be in cleanup_paths
        # because they are owned by the parent process.
        assert upstream.resolve() not in info.cleanup_paths

        # Cleanup simulation: if we were the buggy version, we would delete 'upstream' here.
        f_utils.remove_paths(info.cleanup_paths)

        # Verify upstream is still there
        assert upstream.exists()
        assert (upstream / "templates" / "sub" / "s1").exists()

    def test_pure_upstream_subtemplate_resolution_from_downstream(
        self, tmp_path: Path, patch_user_config
    ):
        """Verify that get_repository can find a template that only exists
        in an upstream repository even when called against downstream."""
        # 1. Setup upstream with a template
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates={
                "sub/upstream_only": {
                    "path": "./templates/sub/upstream_only",
                    "title": "Upstream Only",
                    "description": "Upstream Only",
                }
            },
            groups={
                "sub": {
                    "title": "Sub",
                    "description": "Subtemplates",
                    "templates": ["sub/upstream_only"],
                }
            },
        )
        (upstream / "templates" / "sub" / "upstream_only").mkdir(parents=True)
        (
            upstream / "templates" / "sub" / "upstream_only" / "cookiecutter.json"
        ).write_text("{}")

        # 2. Setup downstream extending it
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
        )

        # 3. Request the upstream template using the downstream repository path
        # This mirrors a hook calling generate_subtemplate for an official
        # template while running in a customized project.
        info = r.get_repository(
            repository=str(downstream),
            template_name="sub/upstream_only",
            template_path="templates/sub/upstream_only",
        )

        # 4. Verify it was correctly found in upstream
        assert info.root_repo_dir == upstream.resolve()
        assert (info.base_repo_dir / "cookiecutter.json").exists()

        from cookieplone.utils import files as f_utils

        f_utils.remove_paths(info.cleanup_paths)

    def test_orphan_template_in_merged_result_fails(
        self, tmp_path: Path, patch_user_config
    ):
        """A downstream that adds a template without putting it in a group
        triggers cross-referential validation on the merged config."""
        upstream = _write_repo(
            tmp_path / "upstream",
            title="Upstream",
            templates=_default_templates("up"),
            groups=_default_groups("up"),
        )
        downstream = _write_repo(
            tmp_path / "downstream",
            title="Downstream",
            extends=str(upstream),
            templates={
                "orphan": {
                    "path": "./templates/orphan",
                    "title": "Orphan",
                    "description": "Orphan, not in any group",
                    "hidden": False,
                },
            },
        )

        with pytest.raises(RuntimeError, match="orphan"):
            r.get_repository_config(downstream)
