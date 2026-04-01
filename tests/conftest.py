import json
import random
import string
from collections.abc import Generator
from pathlib import Path

import pytest
from git import Repo
from pytest import MonkeyPatch

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


@pytest.fixture(scope="session")
def read_data_file(resources_folder):
    def func(filepath: str) -> str:
        data = ""
        path = (resources_folder / filepath).resolve()
        if path.exists():
            data = path.read_text()
        return data

    return func


@pytest.fixture(scope="session")
def read_config_file(read_data_file):
    def func(filepath: str) -> dict:
        raw = read_data_file(filepath)
        data = json.loads(raw)
        return data

    return func


@pytest.fixture(scope="session")
def validate_config(read_config_file):
    def func(config_file: Path):
        from cookieplone.utils.config import validate_config

        schema = read_config_file(config_file)
        return validate_config(schema)

    return func


@pytest.fixture(scope="session")
def project_source(resources_folder) -> Path:
    path = (resources_folder / "templates").resolve()
    return path


@pytest.fixture(scope="module")
def base_template_path(tmpdir_factory):
    """Fixture to prepare a temporary folder."""

    def func() -> Path:
        tmp_path = Path(tmpdir_factory.mktemp("template"))
        return tmp_path

    return func


@pytest.fixture(scope="module")
def template_path(base_template_path, read_data_file):
    """Fixture to prepare a temporary folder with a config file."""

    def func(config_file: str) -> Path:
        path = base_template_path()
        dst_name = "cookiecutter.json" if "v1-" in config_file else "cookieplone.json"
        dst = path / dst_name
        dst.write_text(read_data_file(config_file))
        return path

    return func


@pytest.fixture(scope="session")
def home_folder(tmpdir_factory) -> Generator[Path]:
    """Create a new home folder during the tests."""
    tmp_path = Path(tmpdir_factory.mktemp("myhome"))

    def expanduser(self) -> Path:
        path = f"{self}"
        if path[:1] == "~":
            path = f"{tmp_path}/{path[1:]}"
        return Path(path)

    def home() -> Path:
        return tmp_path

    with MonkeyPatch.context() as m:
        m.setattr(Path, "home", home)
        m.setattr(Path, "expanduser", expanduser)
        m.setenv("HOME", f"{tmp_path}")
        yield tmp_path


@pytest.fixture
def dummy_package(tmpdir_factory, resources_folder) -> Generator[Path]:
    """Create a dummy package to be used in tests."""
    tmp_path = Path(tmpdir_factory.mktemp("dummy_package"))

    src = (resources_folder / "dummy_package").resolve()
    for item in src.rglob("*"):
        if any(part.startswith(".") for part in item.relative_to(src).parts):
            continue
        if item.is_file():
            parent = item.parent.relative_to(src)
            name = item.name
            if name.endswith("_zcml") or name.endswith("_xml"):
                name = name.replace("_", ".")
            dst = tmp_path / parent / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(item.read_text())
    yield tmp_path
