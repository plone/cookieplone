# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from git import Commit, Repo
from git.exc import InvalidGitRepositoryError


def repo_from_path(path: Path) -> Repo | None:
    """Return the repo for the given path."""
    try:
        repo = Repo(path)
    except InvalidGitRepositoryError:
        repo = None
    return repo


def check_path_is_repository(path: Path) -> bool:
    """Check if given path is a Git Repository."""
    return bool(repo_from_path(path))


def initialize_repository(path: Path) -> Repo:
    """Initialize a git repository and add all files."""
    if not check_path_is_repository(path):
        repo = Repo.init(path)
        repo.git.add(path)
    return repo


def get_last_commit(path: Path) -> Commit | None:
    """Return the last commit for a repo."""
    repo = repo_from_path(path)
    return repo.head.commit if repo else None
