import pytest
from git import Commit, Repo

from cookieplone.utils import git


@pytest.fixture
def tmp_repo(tmp_path):
    repo = Repo.init(tmp_path)
    repo.index.add(tmp_path)
    repo.index.commit("test commit")

    return tmp_path


def test_repo_from_path(tmp_repo):
    repo = git.repo_from_path(tmp_repo)
    assert repo == Repo(tmp_repo)


def test_repo_from_path_invalid(tmp_path):
    repo = git.repo_from_path(tmp_path)
    assert repo is None


def test_check_path_is_repository(tmp_repo):
    assert git.check_path_is_repository(tmp_repo)


def test_check_path_is_repository_invalid(tmp_path):
    assert not git.check_path_is_repository(tmp_path)


def test_initialize_repository(tmp_path):
    repo = git.initialize_repository(tmp_path)
    assert isinstance(repo, Repo)


def test_get_last_commit(tmp_repo):
    commit = git.get_last_commit(tmp_repo)
    assert isinstance(commit, Commit)
    assert commit.summary == "test commit"


def test_get_last_commit_invalid(tmp_path):
    assert git.get_last_commit(tmp_path) is None
