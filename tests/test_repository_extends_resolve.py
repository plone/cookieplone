"""Tests for cookieplone.repository._resolve_extends."""

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


def _make_repo(
    path: Path,
    *,
    title: str,
    templates: dict[str, dict[str, Any]] | None = None,
    extends: Any = None,
    groups: dict[str, dict[str, Any]] | None = None,
) -> Path:
    """Materialise a minimal repo with a cookieplone-config.json at *path*."""
    path.mkdir(parents=True, exist_ok=True)
    if templates is None:
        templates = {
            f"{title}_tmpl": {
                "path": f"./templates/{title}",
                "title": f"{title} Template",
                "description": f"Template from {title}",
                "hidden": False,
            },
        }
    if groups is None:
        groups = {
            "main": {
                "title": "Main",
                "description": "Main group",
                "templates": list(templates),
                "hidden": False,
            },
        }
    config: dict[str, Any] = {
        "version": "1.0",
        "title": title,
        "groups": groups,
        "templates": templates,
    }
    if extends is not None:
        config["extends"] = extends
    (path / "cookieplone-config.json").write_text(json.dumps(config))
    return path


def _resolve(extends, tmp_path):
    return r._resolve_extends(
        extends,
        abbreviations={},
        clone_to_dir=tmp_path,
    )


class TestResolveExtends:
    def test_single_level_local(self, tmp_path: Path):
        upstream = _make_repo(tmp_path / "upstream", title="upstream")
        config, repo_dir, cleanup = _resolve(str(upstream), tmp_path)

        assert config["title"] == "upstream"
        assert repo_dir == upstream.resolve()
        assert cleanup == []
        assert "upstream_tmpl" in config["templates"]

    def test_object_form_string_url(self, tmp_path: Path):
        upstream = _make_repo(tmp_path / "upstream", title="upstream")
        config, repo_dir, _ = _resolve({"url": str(upstream)}, tmp_path)

        assert config["title"] == "upstream"
        assert repo_dir == upstream.resolve()

    def test_tag_passed_through(self, tmp_path: Path):
        """The `tag` field in object form must reach determine_repo_dir."""
        upstream = _make_repo(tmp_path / "upstream", title="upstream")
        with patch.object(r, "determine_repo_dir", wraps=r.determine_repo_dir) as spy:
            _resolve({"url": str(upstream), "tag": "2.1.0"}, tmp_path)

        assert spy.call_args.kwargs["checkout"] == "2.1.0"

    def test_transitive_chain(self, tmp_path: Path):
        """A → B → C: merged config has templates from all three layers."""
        c = _make_repo(tmp_path / "c", title="c")
        b = _make_repo(tmp_path / "b", title="b", extends=str(c))

        config, repo_dir, _ = _resolve(str(b), tmp_path)

        assert repo_dir == b.resolve()
        assert {"b_tmpl", "c_tmpl"} <= set(config["templates"])
        # Origins must point at the originating repos.
        assert config[ORIGINS_KEY]["b_tmpl"] == str(b.resolve())
        assert config[ORIGINS_KEY]["c_tmpl"] == str(c.resolve())

    def test_cycle_detected(self, tmp_path: Path):
        a_path = tmp_path / "a"
        b_path = tmp_path / "b"
        # Bootstrap each repo so the paths exist when the other is loaded.
        _make_repo(a_path, title="a")
        _make_repo(b_path, title="b")
        # Now rewrite both with cross-extends.
        _make_repo(a_path, title="a", extends=str(b_path))
        _make_repo(b_path, title="b", extends=str(a_path))

        with pytest.raises(InvalidConfiguration, match="Circular 'extends'"):
            _resolve(str(a_path), tmp_path)

    def test_depth_limit_exceeded(self, tmp_path: Path):
        """A chain longer than MAX_EXTENDS_DEPTH must raise."""
        chain_len = r.MAX_EXTENDS_DEPTH + 2
        repos = [tmp_path / f"repo_{i}" for i in range(chain_len)]
        # Last repo: no extends.
        _make_repo(repos[-1], title=f"repo_{chain_len - 1}")
        # Each previous repo extends the next.
        for i in range(chain_len - 2, -1, -1):
            _make_repo(repos[i], title=f"repo_{i}", extends=str(repos[i + 1]))

        with pytest.raises(InvalidConfiguration, match="depth limit"):
            _resolve(str(repos[0]), tmp_path)

    def test_unreachable_upstream(self, tmp_path: Path):
        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises(RepositoryException, match="Could not resolve 'extends'"):
            _resolve(str(nonexistent), tmp_path)

    def test_empty_extends_raises(self, tmp_path: Path):
        with pytest.raises(InvalidConfiguration):
            _resolve("", tmp_path)

    def test_malformed_extends_raises(self, tmp_path: Path):
        with pytest.raises(InvalidConfiguration):
            _resolve({"tag": "2.0"}, tmp_path)  # missing url

    def test_transitive_template_override_downstream_wins(self, tmp_path: Path):
        """When B redeclares a template from C, the B definition wins."""
        c = _make_repo(
            tmp_path / "c",
            title="c",
            templates={
                "shared": {
                    "path": "./templates/c_shared",
                    "title": "C version",
                    "description": "from c",
                    "hidden": False,
                },
            },
        )
        b = _make_repo(
            tmp_path / "b",
            title="b",
            extends=str(c),
            templates={
                "shared": {
                    "path": "./templates/b_shared",
                    "title": "B version",
                    "description": "from b",
                    "hidden": False,
                },
            },
        )

        config, _, _ = _resolve(str(b), tmp_path)
        assert config["templates"]["shared"]["title"] == "B version"
        assert config[ORIGINS_KEY]["shared"] == str(b.resolve())
