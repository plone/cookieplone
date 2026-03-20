from pathlib import Path

import pytest

from cookieplone.exceptions import RepositoryNotFound
from cookieplone.utils import files


@pytest.fixture
def tmp_paths(tmp_path):
    """Add two folders and return their paths."""
    folders = []
    for idx in range(1, 3):
        folder = tmp_path / f"{idx:02d}"
        folder.mkdir(parents=True)
        folders.append(folder)
    return folders


@pytest.fixture
def tmp_files(tmp_path):
    folder1 = tmp_path / "test" / ".github"
    folder1.mkdir(parents=True)

    file1 = tmp_path / "test" / "test_file.txt"
    file1.touch()

    return file1


def test_remove_paths(tmp_paths: list[Path]):
    assert {p.exists() for p in tmp_paths} == {True}
    files.remove_paths(tmp_paths)
    assert {p.exists() for p in tmp_paths} == {False}


def test_remove_files(tmp_path, tmp_files):
    files_to_remove = tmp_files
    folders_to_remove = tmp_files.parent
    func = files.remove_files

    assert files_to_remove.exists()
    func(tmp_path, [files_to_remove])
    assert not files_to_remove.exists()

    assert folders_to_remove.exists()
    func(tmp_path, [folders_to_remove])
    assert not folders_to_remove.exists()


def test_remove_files_nonexistent_file(tmp_path):
    files_to_remove = ["nonexistent_file.txt"]
    base_path = tmp_path
    assert files.remove_files(base_path, files_to_remove) is None


def test_remove_gha(tmp_files):
    func = files.remove_gha
    base_path = tmp_files.parent

    gha = base_path / ".github"
    assert gha.exists()
    func(base_path)
    assert not gha.exists()


@pytest.mark.parametrize(
    "repository_path,template,max_levels,exists",
    [
        ("templates/add-ons/backend", "docs/starter", 1, False),
        ("templates/add-ons/backend", "docs/starter", 2, True),
        ("templates/add-ons/backend", "docs/starter", 3, True),
        ("templates/add-ons/frontend", "docs/starter", 1, False),
        ("templates/add-ons/frontend", "docs/starter", 2, True),
        ("templates/add-ons/frontend", "docs/starter", 3, True),
        ("templates/project/monorepo", "ci/gh_project", 1, False),
        ("templates/project/monorepo", "ci/gh_project", 2, True),
        ("templates/project/monorepo", "ci/gh_project", 3, True),
    ],
)
def test_get_template_from_path(
    monkeypatch,
    repository_structure,
    get_path,
    repository_path: str,
    template: str,
    max_levels: int,
    exists: bool,
):
    monkeypatch.chdir(repository_structure)
    # Without resolving the path
    result = files.get_template_from_path(repository_path, template, max_levels)
    assert (result is not None) == exists

    path = get_path(repository_path)
    result = files.get_template_from_path(path, template, max_levels)
    assert (result is not None) == exists


@pytest.mark.parametrize(
    "repository_path,key,template,exists",
    [
        (
            "templates/add-ons/backend",
            "__cookieplone_repository_path",
            "docs/starter",
            True,
        ),
        (
            "templates/add-ons/frontend",
            "__cookieplone_repository_path",
            "docs/starter",
            True,
        ),
        (
            "templates/project/monorepo",
            "__cookieplone_repository_path",
            "ci/gh_project",
            True,
        ),
        (
            "templates/add-ons/backend",
            "_repo_dir",
            "docs/starter",
            True,
        ),
        (
            "templates/add-ons/frontend",
            "_repo_dir",
            "docs/starter",
            True,
        ),
        (
            "templates/project/monorepo",
            "_repo_dir",
            "ci/gh_project",
            True,
        ),
        (
            "templates/add-ons/backend",
            "_template",
            "docs/starter",
            True,
        ),
        (
            "templates/add-ons/frontend",
            "_template",
            "docs/starter",
            True,
        ),
        (
            "templates/project/monorepo",
            "_template",
            "ci/gh_project",
            True,
        ),
    ],
)
def test_get_repository_root(
    monkeypatch,
    repository_structure,
    repository_path: str,
    key: str,
    template: str,
    exists: bool,
):
    monkeypatch.chdir(repository_structure)
    # Without resolving the path
    result = files.get_repository_root({key: repository_path}, template)
    assert (result is not None) == exists


@pytest.mark.parametrize(
    "repository_path,key,template",
    [
        (
            "templates/add-ons/backend",
            "_foo",
            "docs/starter",
        ),
        (
            "templates/add-ons/frontend",
            "_foo",
            "docs/starter",
        ),
        (
            "templates/project/monorepo",
            "_foo",
            "ci/gh_project",
        ),
    ],
)
def test_get_repository_root_failure(
    monkeypatch,
    repository_structure,
    repository_path: str,
    key: str,
    template: str,
):
    monkeypatch.chdir(repository_structure)
    with pytest.raises(RepositoryNotFound) as exc:
        files.get_repository_root({key: repository_path}, template)
    assert "RepositoryNotFound" in str(exc)
