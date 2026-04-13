from cookiecutter.exceptions import FailedHookException
from cookieplone import repository
from cookieplone.exceptions import PreFlightException
from cookieplone.exceptions import VersionTooOldException
from cookieplone.repository import _check_min_version
from pathlib import Path

import json
import pytest


@pytest.fixture
def patch_run_pre_prompt_hook(monkeypatch):
    from cookiecutter import hooks

    def hook(repo_dir):
        raise FailedHookException("Pre-Prompt Hook script failed")

    monkeypatch.setattr(hooks, "run_pre_prompt_hook", hook)
    yield


def test__run_pre_hook_failure(patch_run_pre_prompt_hook, project_source):
    func = repository._run_pre_hook
    with pytest.raises(PreFlightException) as exc:
        func(project_source, project_source, accept_hooks=True)
    assert isinstance(exc.value, PreFlightException) is True
    msg = "Sanity checks failed.\nPlease review the errors above and try again."
    assert exc.value.message == msg


def test__run_pre_hook_passes(project_source):
    func = repository._run_pre_hook
    result = func(project_source, project_source, accept_hooks=True)
    assert isinstance(result, Path)


def _write_repo_config(root: Path, config_section: dict) -> None:
    """Write a minimal cookieplone-config.json with the given config section."""
    payload = {
        "version": "1.0",
        "title": "Test Templates",
        "groups": {
            "main": {
                "title": "Main",
                "description": "Main",
                "templates": ["project"],
                "hidden": False,
            },
        },
        "templates": {
            "project": {
                "path": "./templates/project",
                "title": "Project",
                "description": "A project",
                "hidden": False,
            },
        },
        "config": config_section,
    }
    (root / "cookieplone-config.json").write_text(json.dumps(payload))


class TestGetRepositoryConfigExtraction:
    """Verify get_repository extracts renderer + global_versions correctly."""

    def _patch_repo_setup(self, monkeypatch, repo_dir):
        """Stub out the cloning / pre-prompt machinery so the test stays local."""
        monkeypatch.setattr(
            repository,
            "get_user_config",
            lambda **_: {
                "abbreviations": {},
                "cookiecutters_dir": str(repo_dir.parent),
                "replay_dir": str(repo_dir.parent),
            },
        )
        monkeypatch.setattr(
            repository,
            "determine_repo_dir",
            lambda **_: (repo_dir, False),
        )
        monkeypatch.setattr(
            repository,
            "_run_pre_hook",
            lambda base, repo, accept_hooks: repo,
        )

    def test_extracts_renderer_from_repo_config(self, tmp_path, monkeypatch):
        """get_repository populates RepositoryInfo.renderer from the config."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        _write_repo_config(repo_dir, {"renderer": "rich"})
        self._patch_repo_setup(monkeypatch, repo_dir)

        info = repository.get_repository(
            repository=str(repo_dir),
            template_name="project",
            template_path="",
        )
        assert info.renderer == "rich"

    def test_renderer_defaults_to_empty(self, tmp_path, monkeypatch):
        """Missing renderer key results in an empty string, not None."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        _write_repo_config(repo_dir, {"versions": {"foo": "bar"}})
        self._patch_repo_setup(monkeypatch, repo_dir)

        info = repository.get_repository(
            repository=str(repo_dir),
            template_name="project",
            template_path="",
        )
        assert info.renderer == ""
        assert info.global_versions == {"foo": "bar"}

    def test_no_repo_config_means_empty_renderer(self, tmp_path, monkeypatch):
        """A repo without cookieplone-config.json yields an empty renderer."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        # Provide a legacy cookiecutter.json so _repository_has_config is True
        (repo_dir / "cookiecutter.json").write_text("{}")
        self._patch_repo_setup(monkeypatch, repo_dir)

        info = repository.get_repository(
            repository=str(repo_dir),
            template_name="project",
            template_path="",
        )
        assert info.renderer == ""


class TestCheckMinVersion:
    """Tests for _check_min_version."""

    def test_no_min_version_key(self):
        """No-op when min_version is absent."""
        _check_min_version({})

    def test_empty_min_version(self):
        """No-op when min_version is an empty string."""
        _check_min_version({"min_version": ""})

    def test_version_satisfied(self, monkeypatch):
        """No error when installed version meets the requirement."""
        monkeypatch.setattr("cookieplone.__version__", "2.1.0")
        _check_min_version({"min_version": "2.0.0"})

    def test_version_exact_match(self, monkeypatch):
        """No error when installed version equals min_version."""
        monkeypatch.setattr("cookieplone.__version__", "2.0.0")
        _check_min_version({"min_version": "2.0.0"})

    def test_version_too_old(self, monkeypatch):
        """Raises VersionTooOldException when installed version is older."""
        monkeypatch.setattr("cookieplone.__version__", "1.3.0")
        with pytest.raises(VersionTooOldException, match=r"cookieplone >= 2\.0\.0"):
            _check_min_version({"min_version": "2.0.0"})

    def test_error_message_includes_versions(self, monkeypatch):
        """Error message includes both the required and installed versions."""
        monkeypatch.setattr("cookieplone.__version__", "1.5.0")
        with pytest.raises(VersionTooOldException, match=r"1\.5\.0") as exc_info:
            _check_min_version({"min_version": "2.0.0"})
        assert "uvx --no-cache cookieplone@2.0.0" in exc_info.value.message

    def test_prerelease_satisfied(self, monkeypatch):
        """Pre-release installed version satisfies a pre-release requirement."""
        monkeypatch.setattr("cookieplone.__version__", "2.0.0a2")
        _check_min_version({"min_version": "2.0.0a1"})

    def test_prerelease_too_old(self, monkeypatch):
        """Pre-release installed version fails against a newer pre-release."""
        monkeypatch.setattr("cookieplone.__version__", "2.0.0a1")
        with pytest.raises(VersionTooOldException):
            _check_min_version({"min_version": "2.0.0a2"})

    def test_dev_version_satisfies_prerelease(self, monkeypatch):
        """Dev version (e.g. 2.0.0a2.dev0) satisfies an older pre-release."""
        monkeypatch.setattr("cookieplone.__version__", "2.0.0a2.dev0")
        _check_min_version({"min_version": "2.0.0a1"})

    def test_get_repository_raises_on_min_version(self, tmp_path, monkeypatch):
        """get_repository raises VersionTooOldException when min_version fails."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        _write_repo_config(repo_dir, {"min_version": "99.0.0"})
        monkeypatch.setattr(
            repository,
            "get_user_config",
            lambda **_: {
                "abbreviations": {},
                "cookiecutters_dir": str(repo_dir.parent),
                "replay_dir": str(repo_dir.parent),
            },
        )
        monkeypatch.setattr(
            repository,
            "determine_repo_dir",
            lambda **_: (repo_dir, False),
        )
        monkeypatch.setattr(
            repository,
            "_run_pre_hook",
            lambda base, repo, accept_hooks: repo,
        )
        with pytest.raises(VersionTooOldException, match=r"cookieplone >= 99\.0\.0"):
            repository.get_repository(
                repository=str(repo_dir),
                template_name="project",
                template_path="",
            )
