import random
import string
from collections import OrderedDict
from pathlib import Path
from typing import Any

import pytest
from git import Repo

pytest_plugins = "pytester"


@pytest.fixture(scope="session")
def resources_folder():
    path = (Path(__file__).parent / "_resources").resolve()

    return path


@pytest.fixture()
def tmp_repo(tmp_path):
    repo = Repo.init(tmp_path)
    repo.index.add(tmp_path)
    repo.index.commit("test commit")

    return tmp_path


@pytest.fixture()
def no_repo(tmp_path):
    letters = string.ascii_lowercase
    sub_path = "".join(random.choice(letters) for _ in range(20))  # noQA: S311
    path = tmp_path / sub_path
    path.mkdir(parents=True)
    return path


@pytest.fixture()
def read_data_file(resources_folder):
    def func(filepath: str) -> str:
        data = ""
        path = (resources_folder / filepath).resolve()
        if path.exists():
            data = path.read_text()
        return data

    return func


@pytest.fixture(scope="session")
def project_source(resources_folder) -> Path:
    path = (resources_folder / "templates").resolve()
    return path


@pytest.fixture(scope="session")
def context() -> OrderedDict[str, Any]:
    return OrderedDict({
        "title": "Test Project",
        "description": "A test Project",
        "language_code": ["en", "de", "es", "pt-br", "nl", "fi", "it", "sv"],
        "hostname": "foo.example.com",
        "__prompts__": {
            "title": "Project Title",
            "project_slug": "Project Slug (Used for repository id)",
            "hostname": "Project URL (without protocol)",
            "description": "Project Description",
            "language_code": {
                "__prompt__": "Language",
                "en": "English",
                "de": "Deutsch",
                "es": "Español",
                "fi": "Suomi",
                "it": "Italiano",
                "pt-br": "Português (Brasil)",
                "nl": "Nederlands",
                "sv": "Svenska",
            },
        },
        "__validators__": {
            "title": "cookieplone.validators.non_empty",
            "hostname": "cookieplone.validators.hostname",
            "language_code": "cookieplone.validators.language_code",
            "plone_version": "cookieplone.validators.plone_version",
            "volto_version": "cookieplone.validators.volto_version",
        },
        "_hidden": "This should be removed",
        "__folder_name": "test-project",
        "__generator_sha": "44f4a492fdf40acb385227b0564b7c62d22bd8d9",
        "__cookieplone_template": "project",
        "__generator_signature": (
            "Generated using [Cookieplone "
            "(0.9.11.dev0)](https://github.com/plone/cookieplone) and "
            "[cookieplone-templates "
            "(44f4a49)](https://github.com/plone/cookieplone-templates/commit/"
            "44f4a492fdf40acb385227b0564b7c62d22bd8d9)"
        ),
    })
