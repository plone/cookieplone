"""Shared fixtures for generator tests."""

from unittest.mock import MagicMock

import pytest

from cookieplone._types import RepositoryInfo, RunConfig
from cookieplone.config.state import CookieploneState


@pytest.fixture()
def run_config(tmp_path):
    """A minimal RunConfig."""
    return RunConfig(
        output_dir=tmp_path,
        no_input=True,
        accept_hooks=True,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        keep_project_on_failure=False,
    )


@pytest.fixture()
def repository_info(tmp_path):
    """A minimal RepositoryInfo."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    return RepositoryInfo(
        repository="gh:plone/cookieplone-templates",
        base_repo_dir=repo_dir,
        repo_dir=repo_dir,
        root_repo_dir=repo_dir,
        replay_dir=tmp_path / "replay",
        template_name="project",
        checkout="",
        accept_hooks=True,
        config_dict={},
        cleanup_paths=[],
    )


@pytest.fixture()
def state():
    """A minimal CookieploneState."""
    return CookieploneState(
        schema={"version": "2.0", "properties": {}},
        data={"cookiecutter": {"title": "Test"}},
        root_key="cookiecutter",
        extensions=[],
    )


@pytest.fixture()
def mock_cookieplone_inner(monkeypatch):
    """Patch cookieplone.generator.main._cookieplone."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.main._cookieplone", mock)
    return mock


@pytest.fixture()
def mock_write_answers(monkeypatch):
    """Patch cookieplone.generator.answers.write_answers."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.answers.write_answers", mock)
    return mock


@pytest.fixture()
def mock_get_repository(monkeypatch):
    """Patch cookieplone.generator.get_repository."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.get_repository", mock)
    return mock


@pytest.fixture()
def mock_generate(monkeypatch):
    """Patch cookieplone.generator.generate."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.generate", mock)
    return mock


@pytest.fixture()
def mock_console(monkeypatch):
    """Patch cookieplone.generator.console."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.console", mock)
    return mock


@pytest.fixture()
def mock_get_repository_root(monkeypatch):
    """Patch cookieplone.generator.files.get_repository_root."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.files.get_repository_root", mock)
    return mock


@pytest.fixture()
def mock_remove_internal_keys(monkeypatch):
    """Patch cookieplone.generator.answers.remove_internal_keys."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.answers.remove_internal_keys", mock)
    return mock


@pytest.fixture()
def mock_remove_files(monkeypatch):
    """Patch cookieplone.generator.files.remove_files."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.files.remove_files", mock)
    return mock


@pytest.fixture()
def mock_load_replay(monkeypatch):
    """Patch cookieplone.generator.load_replay."""
    mock = MagicMock(return_value={})
    monkeypatch.setattr("cookieplone.generator.load_replay", mock)
    return mock


@pytest.fixture()
def mock_generate_state(monkeypatch, state):
    """Patch cookieplone.generator.generate_state to return the state fixture."""
    mock = MagicMock(return_value=state)
    monkeypatch.setattr("cookieplone.generator.generate_state", mock)
    return mock


@pytest.fixture()
def mock_cookieplone_entry(monkeypatch):
    """Patch cookieplone.generator.cookieplone (the main.cookieplone entry)."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.cookieplone", mock)
    return mock


@pytest.fixture()
def mock_dump_replay(monkeypatch):
    """Patch cookieplone.generator.cookiecutter.dump_replay."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.generator.cookiecutter.dump_replay", mock)
    return mock


@pytest.fixture()
def repository_info_with_config(tmp_path):
    """A RepositoryInfo with default_context in config_dict."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    return RepositoryInfo(
        repository="gh:plone/cookieplone-templates",
        base_repo_dir=repo_dir,
        repo_dir=repo_dir,
        root_repo_dir=repo_dir,
        replay_dir=tmp_path / "replay",
        template_name="project",
        checkout="",
        accept_hooks=True,
        config_dict={"default_context": {}},
        cleanup_paths=[],
    )
