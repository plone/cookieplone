from git import Commit, Repo

from cookieplone.utils import git


def test_repo_from_path(tmp_repo):
    repo = git.repo_from_path(tmp_repo)
    assert repo == Repo(tmp_repo)


def test_repo_from_path_invalid(no_repo):
    repo = git.repo_from_path(no_repo)
    assert repo is None


def test_check_path_is_repository(tmp_repo):
    assert git.check_path_is_repository(tmp_repo)


def test_check_path_is_repository_invalid(no_repo):
    assert not git.check_path_is_repository(no_repo)


def test_initialize_repository_existing_repo(tmp_repo):
    repo = git.initialize_repository(tmp_repo)
    assert isinstance(repo, Repo)


def test_initialize_repository_new_repo(no_repo):
    repo = git.initialize_repository(no_repo)
    assert isinstance(repo, Repo)
    assert repo.active_branch.name == "main"


def test_get_last_commit(tmp_repo):
    commit = git.get_last_commit(tmp_repo)
    assert isinstance(commit, Commit)
    assert commit.summary == "test commit"


def test_get_last_commit_invalid(no_repo):
    assert git.get_last_commit(no_repo) is None
