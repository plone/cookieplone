"""Regression tests for :mod:`cookieplone.templates.bake`."""

from cookieplone.templates.bake import _discover_global_versions
from pathlib import Path


class TestDiscoverGlobalVersions:
    def test_returns_versions_when_repo_config_present(self, resources_folder: Path):
        """Walk upward from a template path and pick up ``config.versions``."""
        repo_root = (resources_folder / "templates_repo_config").resolve()
        template_path = repo_root / "templates" / "projects" / "monorepo"
        result = _discover_global_versions(template_path)
        assert result == {"gha_version_checkout": "v6"}

    def test_returns_empty_when_no_repo_config(self, tmp_path: Path):
        """Return an empty dict when no ``cookieplone-config.json`` is found."""
        template_path = tmp_path / "standalone" / "template"
        template_path.mkdir(parents=True)
        assert _discover_global_versions(template_path) == {}

    def test_returns_empty_when_config_is_invalid(self, tmp_path: Path):
        """Return an empty dict when the repo config fails validation."""
        (tmp_path / "cookieplone-config.json").write_text("{}")
        template_path = tmp_path / "templates" / "project"
        template_path.mkdir(parents=True)
        assert _discover_global_versions(template_path) == {}
