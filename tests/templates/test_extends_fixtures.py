"""Tests for cookieplone.templates.extends_fixtures."""

from __future__ import annotations

from cookieplone.templates import extends_fixtures
from pathlib import Path
from typing import Any

import json
import pytest


def _make_repo(
    path: Path,
    *,
    title: str,
    templates: dict[str, dict[str, Any]] | None = None,
    extends: Any = None,
) -> Path:
    """Materialise a minimal cookieplone repo at *path*."""
    path.mkdir(parents=True, exist_ok=True)
    if templates is None:
        templates = {
            f"{title}_tmpl": {
                "path": f"./templates/{title}",
                "title": f"{title} template",
                "description": f"Template from {title}",
                "hidden": False,
            },
        }
    config: dict[str, Any] = {
        "version": "1.0",
        "title": title,
        "groups": {
            "main": {
                "title": "Main",
                "description": "Main group",
                "templates": list(templates),
                "hidden": False,
            },
        },
        "templates": templates,
    }
    if extends is not None:
        config["extends"] = extends
    (path / "cookieplone-config.json").write_text(json.dumps(config))
    return path


# ---- In-process unit tests ---------------------------------------------------


class TestDownstreamRepoDir:
    def test_defaults_to_cwd(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        # Call the underlying function via __wrapped__ -- pytest fixture
        # objects don't expose their function directly without a request.
        assert extends_fixtures.downstream_repo_dir.__wrapped__() == tmp_path.resolve()


class TestUpstreamCheckout:
    def test_defaults_to_none(self):
        assert extends_fixtures.upstream_checkout.__wrapped__() is None


# ---- pytester end-to-end tests ----------------------------------------------


def _make_pure_downstream(path: Path, *, extends: str) -> Path:
    """Materialise a downstream that only declares ``extends`` (no local
    templates or groups).  Mirrors the ``test_pure_extension_no_templates``
    schema case.
    """
    path.mkdir(parents=True, exist_ok=True)
    config = {
        "version": "1.0",
        "title": "Downstream",
        "extends": extends,
    }
    (path / "cookieplone-config.json").write_text(json.dumps(config))
    return path


@pytest.fixture
def synthetic_pair(pytester):
    """Make an upstream + pure-extension downstream pair in
    *pytester._path* and return their resolved paths.
    """
    upstream = _make_repo(pytester.path / "upstream", title="upstream")
    downstream = _make_pure_downstream(
        pytester.path / "downstream", extends=str(upstream.resolve())
    )
    return upstream.resolve(), downstream.resolve()


def _write_conftest_pointing_at(downstream_path: Path, pytester) -> None:
    """Write a synthetic conftest into *pytester* that overrides
    ``downstream_repo_dir`` so the fixture resolves the synthetic pair.

    Mirrors the pattern used by ``tests/templates/test_fixtures.py``.
    """
    pytester.makeconftest(
        f"""
        from pathlib import Path
        import pytest

        @pytest.fixture(scope="session")
        def downstream_repo_dir() -> Path:
            return Path({str(downstream_path)!r})
        """
    )


def test_upstream_repo_dir_resolves(pytester, synthetic_pair):
    upstream, downstream = synthetic_pair
    _write_conftest_pointing_at(downstream, pytester)
    pytester.makepyfile(
        f"""
        def test_resolved(upstream_repo_dir):
            assert upstream_repo_dir is not None
            assert str(upstream_repo_dir) == {str(upstream)!r}
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_upstream_repo_dir_yields_none_without_extends(pytester):
    """When the downstream declares no extends, the fixture yields None
    and emits a warning.
    """
    bare = _make_repo(pytester.path / "bare", title="bare")  # no extends
    _write_conftest_pointing_at(bare.resolve(), pytester)
    pytester.makepyfile(
        """
        def test_no_upstream(upstream_repo_dir):
            assert upstream_repo_dir is None
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)


def test_cli_upstream_dir_short_circuits(pytester, tmp_path):
    """``--cookieplone-upstream-dir`` bypasses resolution; the fixture
    yields the supplied path verbatim even when the downstream has no
    ``cookieplone-config.json``.
    """
    forced = tmp_path / "local-checkout"
    forced.mkdir()
    # Note: no downstream config required when the CLI override is set.
    pytester.makepyfile(
        f"""
        def test_forced(upstream_repo_dir):
            assert str(upstream_repo_dir) == {str(forced.resolve())!r}
        """
    )
    result = pytester.runpytest(f"--cookieplone-upstream-dir={forced}")
    result.assert_outcomes(passed=1)


def test_upstream_checkout_override_is_passed_through(pytester, synthetic_pair):
    """When ``upstream_checkout`` is overridden, the resolver receives
    that tag instead of any tag declared in the downstream's extends.

    We assert this by spying on ``determine_repo_dir``: at least one
    call's ``checkout`` kwarg must be the override value.  The spy is
    installed at session scope so it's in place before the session
    fixture resolves.
    """
    _upstream, downstream = synthetic_pair
    pytester.makeconftest(
        f"""
        from pathlib import Path
        import pytest

        @pytest.fixture(scope="session")
        def downstream_repo_dir() -> Path:
            return Path({str(downstream)!r})

        @pytest.fixture(scope="session")
        def upstream_checkout() -> str:
            return "2.1.0"

        @pytest.fixture(scope="session", autouse=True)
        def _spy_determine_repo_dir():
            from cookieplone import repository as r
            seen = []
            original = r.determine_repo_dir
            def wrapper(**kwargs):
                seen.append(kwargs)
                return original(**kwargs)
            r.determine_repo_dir = wrapper
            yield seen
            r.determine_repo_dir = original
        """
    )
    pytester.makepyfile(
        """
        def test_checkout_passed(upstream_repo_dir, _spy_determine_repo_dir):
            assert upstream_repo_dir is not None
            assert any(
                call.get("checkout") == "2.1.0"
                for call in _spy_determine_repo_dir
            )
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)


def test_merged_repository_config_with_extends(pytester, synthetic_pair):
    """When the downstream extends an upstream, the merged config
    carries the upstream's templates."""
    _upstream, downstream = synthetic_pair
    _write_conftest_pointing_at(downstream, pytester)
    pytester.makepyfile(
        """
        def test_merged(merged_repository_config):
            assert merged_repository_config is not None
            assert "upstream_tmpl" in merged_repository_config["templates"]
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)


def test_merged_repository_config_without_extends(pytester):
    """When the downstream has no extends, the fixture returns the raw
    downstream config unchanged."""
    bare = _make_repo(pytester.path / "bare", title="bare")
    _write_conftest_pointing_at(bare.resolve(), pytester)
    pytester.makepyfile(
        """
        def test_raw(merged_repository_config):
            assert merged_repository_config is not None
            assert merged_repository_config["title"] == "bare"
            assert "bare_tmpl" in merged_repository_config["templates"]
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)


def test_merged_repository_config_returns_copy(pytester, synthetic_pair):
    """Mutating the returned dict must not affect a subsequent test."""
    _upstream, downstream = synthetic_pair
    _write_conftest_pointing_at(downstream, pytester)
    pytester.makepyfile(
        """
        def test_first(merged_repository_config):
            merged_repository_config["title"] = "mutated"

        def test_second(merged_repository_config):
            # Same session, but a fresh copy per test.
            assert merged_repository_config["title"] != "mutated"
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=2)


def test_template_layers_with_extends(pytester, synthetic_pair):
    """When extending an upstream, every templates' layer list is
    present in the sidecar."""
    _upstream, downstream = synthetic_pair
    _write_conftest_pointing_at(downstream, pytester)
    pytester.makepyfile(
        """
        def test_layers(template_layers):
            assert "upstream_tmpl" in template_layers
            layers = template_layers["upstream_tmpl"]
            assert len(layers) >= 1
            # Each layer is [repo_dir, relative_path].
            assert len(layers[0]) == 2
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)


def test_template_layers_empty_without_extends(pytester):
    """When the downstream has no extends, the sidecar is empty."""
    bare = _make_repo(pytester.path / "bare", title="bare")
    _write_conftest_pointing_at(bare.resolve(), pytester)
    pytester.makepyfile(
        """
        def test_no_layers(template_layers):
            assert template_layers == {}
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)


def test_upstream_repo_dir_populates_resolution_cache(pytester, synthetic_pair):
    """The fixture must populate ``_RESOLUTION_CACHE`` so a subsequent
    ``get_repository_config(downstream_repo_dir)`` call inside a test
    does not re-clone the upstream.
    """
    _upstream, downstream = synthetic_pair
    _write_conftest_pointing_at(downstream, pytester)
    pytester.makepyfile(
        f"""
        from cookieplone import repository as r
        def test_cache_populated(upstream_repo_dir):
            assert upstream_repo_dir is not None
            assert {str(downstream)!r} in r._RESOLUTION_CACHE
        """
    )
    result = pytester.runpytest("-W", "ignore")
    result.assert_outcomes(passed=1)
