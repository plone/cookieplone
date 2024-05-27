import random
import string
from pathlib import Path

import pytest
from git import Repo

pytest_plugins = "pytester"


@pytest.fixture()
def tmp_repo(tmp_path):
    repo = Repo.init(tmp_path)
    repo.index.add(tmp_path)
    repo.index.commit("test commit")

    return tmp_path


@pytest.fixture()
def no_repo(tmp_path):
    sub_path = "".join(random.choice(string.ascii_lowercase) for _ in range(20))  # noQA:S311
    path = tmp_path / sub_path
    path.mkdir(parents=True)
    return path


@pytest.fixture()
def read_data_file():
    def func(filepath: str) -> str:
        data = ""
        cwd = Path.cwd()
        path = (cwd / "tests" / "_resources" / filepath).resolve()
        if path.exists():
            data = path.read_text()
        return data

    return func


@pytest.fixture(scope="session")
def project_source() -> Path:
    path = (Path(__file__).parent / "_resources" / "templates").resolve()
    return path
