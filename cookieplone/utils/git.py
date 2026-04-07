# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from cookieplone.logger import logger
from dataclasses import dataclass
from git import Commit
from git import Git
from git import GitConfigParser
from git import Repo
from git.exc import GitCommandError
from git.exc import InvalidGitRepositoryError
from pathlib import Path
from typing import cast


@dataclass
class GitUserInfo:
    name: str = ""
    email: str = ""


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
        try:
            initial_branch = Git().config("init.defaultBranch")
        except GitCommandError:
            initial_branch = "main"
        repo = Repo.init(path, initial_branch=initial_branch)
        repo.git.add(path)
    else:
        repo = Repo(path)
    return repo


def get_last_commit(path: Path) -> Commit | None:
    """Return the last commit for a repo."""
    repo = repo_from_path(path)
    return repo.head.commit if repo else None


def get_user_info() -> GitUserInfo:
    """Return git user info by reading available config levels.

    Checks the repository config (via :meth:`~git.Repo.config_reader`) when
    the current directory is inside a git repo, then falls through to the
    ``user``, ``global``, and ``system`` levels using
    :class:`~git.config.GitConfigParser` as a context manager.

    .. note::
        ``GitConfigParser(config_level="repository")`` cannot be used
        standalone — it requires a :class:`~git.Repo` object internally and
        will raise :exc:`ValueError` before ``_read_only`` is initialised,
        leaving a partially-constructed object that triggers an
        :exc:`AttributeError` in ``__del__`` when the GC collects it.  We
        therefore read the repository level through ``Repo.config_reader()``.
    """
    name = ""
    email = ""

    # Repository-level config requires a Repo object
    repo = repo_from_path(Path.cwd())
    if repo:
        try:
            with repo.config_reader() as conf:
                if name_ := conf.get_value("user", "name", ""):
                    name = cast(str, name_)
                if email_ := conf.get_value("user", "email", ""):
                    email = cast(str, email_)
        except Exception as e:
            logger.debug(f"Could not read repository git config: {e}")

    for level in ["user", "global", "system"]:
        if name and email:
            break
        try:
            with GitConfigParser(config_level=level, read_only=True) as conf:
                if not name and (name_ := conf.get_value("user", "name", "")):
                    name = cast(str, name_)
                if not email and (email_ := conf.get_value("user", "email", "")):
                    email = cast(str, email_)
        except (ValueError, AttributeError):
            continue
    return GitUserInfo(name, email)
