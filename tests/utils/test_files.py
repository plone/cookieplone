import pytest

from cookieplone.utils import files


@pytest.fixture
def tmp_files(tmp_path):
    folder1 = tmp_path / "test" / ".github"
    folder1.mkdir(parents=True)

    file1 = tmp_path / "test" / "test_file.txt"
    file1.touch()

    return file1


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
