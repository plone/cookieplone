from pathlib import Path
from typing import Any

import pytest

from cookieplone.config import user as config

CONFIG_FILES: dict[str, dict] = {
    "badconfig.yml": {"src": "badconfig", "contents": {}},
    "badconfig.yaml": {"src": "badconfig_list", "contents": {}},
    ".cookieplonerc": {
        "src": "cookieplonerc",
        "contents": {
            "default_context": {
                "author": "Nahla Ake",
                "email": "ake@academy.starfleet",
                "github_organization": "academy",
            },
        },
    },
    ".cookiecutterrc": {
        "src": "cookiecutterrc",
        "contents": {
            "default_context": {
                "author": "Commander Tomalak",
                "email": "tomalak@mil.rse",
                "github_organization": "rse",
            },
        },
    },
    "my-config.yaml": {
        "src": "userconfig",
        "contents": {
            "default_context": {
                "author": "Jean Luc Picard",
                "email": "jl@diplo.starfleet",
                "github_organization": "starfleet",
            },
        },
    },
}

ALL_FILES = list(CONFIG_FILES)
BAD_FILES = [name for name in ALL_FILES if name.startswith("badconfig")]

DEFAULT_CONFIG = config._get_default_config()


CONFIG_VALUES = {""}


@pytest.fixture
def populate_home_folder(home_folder, monkeypatch, resources_folder):
    """Fixture to prepare a temporary folder."""

    cleanup: list[Path] = []

    def func(files: list[str], env_vars: dict[str, str]) -> Path:

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        for name in files:
            filename = CONFIG_FILES[name]["src"]
            src = resources_folder / "user_config" / filename
            dst = home_folder / name
            dst.write_text(src.read_text())
            cleanup.append(dst)
        return home_folder

    yield func
    for filepath in cleanup:
        filepath.unlink()


@pytest.fixture
def merge_default():
    def func(folder, expected: dict[str, Any]) -> dict[str, Any]:
        default = config._get_default_config()
        default.update(expected)
        return default

    return func


@pytest.mark.parametrize(
    "path,env_vars,expected",
    (
        ("~/foo.txt", {}, "#HOME#/foo.txt"),
        ("bar.txt", {}, "#CWD#/bar.txt"),
        ("${ROOT}/foo.txt", {"ROOT": "/a-path"}, "/a-path/foo.txt"),
        ("~/${NAME}.txt", {"NAME": "bar"}, "#HOME#/bar.txt"),
        ("~.${NAME}.txt", {"NAME": "bar"}, "#HOME#/.bar.txt"),
    ),
)
def test__expand_path(populate_home_folder, work_dir, path, env_vars, expected):
    home_folder = populate_home_folder([], env_vars)
    result = config._expand_path(path)
    expected = expected.replace("#HOME#", f"{home_folder}").replace(
        "#CWD#", f"{work_dir}"
    )
    assert isinstance(result, Path)
    assert result == Path(expected)


@pytest.mark.parametrize(
    "description,files,env_vars,config_file_,default_config,expected",
    (
        ("Just default settings", [], {}, "", {}, {}),
        (
            "Just default settings, if provided default_config is not a dict",
            [],
            {},
            "",
            ["something"],
            {},
        ),
        ("Just default settings (default_config=False)", [], {}, "", False, {}),
        (
            "Passing a default config has priority",
            [],
            {},
            "",
            {"default_context": {"email": "foo@bar"}},
            {"default_context": {"email": "foo@bar"}},
        ),
        (
            ".cookieplonerc has priority",
            ALL_FILES,
            {},
            "",
            False,
            CONFIG_FILES[".cookieplonerc"]["contents"],
        ),
        (
            ".cookiecutterrc has priority if no .cookieplonerc is found",
            [f for f in ALL_FILES if f != ".cookieplonerc"],
            {},
            "",
            False,
            CONFIG_FILES[".cookiecutterrc"]["contents"],
        ),
        (
            "Passing valid config_file location takes priority over default locations",
            ALL_FILES,
            {},
            "~/my-config.yaml",
            {},
            CONFIG_FILES["my-config.yaml"]["contents"],
        ),
        (
            "Passing valid COOKIEPLONE_CONFIG env var",
            ALL_FILES,
            {"COOKIEPLONE_CONFIG": "~/my-config.yaml"},
            "",
            False,
            CONFIG_FILES["my-config.yaml"]["contents"],
        ),
        (
            "Passing valid COOKIEPLONE_CONFIG env var will be picked first",
            ALL_FILES,
            {
                "COOKIEPLONE_CONFIG": "~/my-config.yaml",
                "COOKIECUTTER_CONFIG": "~/.cookieplonerc",
            },
            "",
            False,
            CONFIG_FILES["my-config.yaml"]["contents"],
        ),
        (
            "Passing valid COOKIECUTTER_CONFIG env var will be picked first",
            ALL_FILES,
            {
                "COOKIECUTTER_CONFIG": "~/my-config.yaml",
            },
            "",
            False,
            CONFIG_FILES["my-config.yaml"]["contents"],
        ),
        (
            "Failure to process a file will return .cookieplonerc",
            ALL_FILES,
            {
                "COOKIEPLONE_CONFIG": "~/badconfig.yml",
            },
            "",
            False,
            CONFIG_FILES[".cookieplonerc"]["contents"],
        ),
        (
            "Failure to process a file will return .cookieplonerc",
            ALL_FILES,
            {
                "COOKIECUTTER_CONFIG": "~/badconfig.yml",
            },
            "",
            False,
            CONFIG_FILES[".cookieplonerc"]["contents"],
        ),
        (
            "Failure to process a file will return .cookieplonerc",
            ALL_FILES,
            {},
            "~/badconfig.yaml",
            False,
            CONFIG_FILES[".cookieplonerc"]["contents"],
        ),
    ),
)
def test_get_user_config(
    populate_home_folder,
    merge_default,
    description: str,
    files: list[str],
    env_vars: dict[str, str],
    config_file_: str,
    default_config: dict | bool,
    expected: dict,
):
    home_folder = populate_home_folder(files, env_vars)
    config_file = config_file_ if config_file_ else None
    result = config.get_user_config(config_file, default_config)
    expected = merge_default(home_folder, expected)
    assert result == expected, f"❗ {description}: Failed"


@pytest.mark.parametrize(
    "config_file_,expected",
    (
        ("~/badconfig.yml", "Unable to parse YAML file"),
        ("~/badconfig.yaml", "Top-level element of YAML file"),
    ),
)
def test_get_config_failures(populate_home_folder, config_file_: str, expected: str):
    from cookieplone.exceptions import InvalidConfiguration

    populate_home_folder(BAD_FILES, {})
    config_file: Path = config._expand_path(config_file_)
    with pytest.raises(InvalidConfiguration) as exc:
        config.get_config(config_file)
    assert expected in str(exc)
