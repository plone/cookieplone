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
