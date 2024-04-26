import random
import string

import pytest
from git import Repo


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
