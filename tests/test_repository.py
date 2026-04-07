import json
from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException

from cookieplone import repository
from cookieplone.exceptions import PreFlightException


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
