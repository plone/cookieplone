import sys

import pytest

from cookieplone.utils import commands


@pytest.fixture
def mock_get_command_version(monkeypatch):
    def func(raw_version):
        def patch(cmd: str):
            return raw_version

        monkeypatch.setattr(commands, "_get_command_version", patch)

    return func


@pytest.mark.parametrize(
    "value,expected",
    [
        ["v20.11.1", "20"],
        ["v22.11.1", "22"],
        ["v22.11", ""],
        ["v22", ""],
        ["22.11.1", ""],
        ["22", ""],
        ["foo", ""],
    ],
)
def test_parse_node_major_version(value: str, expected: str):
    func = commands._parse_node_major_version
    assert func(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ["Docker version 25.0.3, build 4debf41", "25.0"],
        ["Docker version 25.0.3", "25.0"],
        [" Docker version 25.0.3", "25.0"],
        [" Docker version 25.0.3  ", "25.0"],
        ["25.0.3", ""],
        ["25.0", ""],
        ["25", ""],
        ["foo", ""],
    ],
)
def test_parse_docker_version(value: str, expected: str):
    func = commands._parse_docker_version
    assert func(value) == expected


@pytest.mark.parametrize(
    "cli,expected",
    [
        ["git", ""],
        ["python", ""],
        ["kowabunga0123", "Command kowabunga0123 is not available."],
    ],
)
def test_check_command_is_available(cli: str, expected: str):
    func = commands.check_command_is_available
    assert func(cli) == expected


@pytest.mark.parametrize(
    "versions,expected",
    [
        [[], ""],
        [
            [
                "3.10",
                "3.11",
                "3.12",
                "3.13",
            ],
            "",
        ],
        [
            [
                "1.5",
                "2.4",
            ],
            f"Python version is not supported: Got {sys.version}",
        ],
    ],
)
def test_check_python_version(versions: list[str], expected: str):
    func = commands.check_python_version
    assert func(versions) == expected


@pytest.mark.parametrize(
    "raw_version,min_version,expected",
    [
        ["", "", "Docker not found."],
        ["", "20.04", "Docker not found."],
        ["Docker version 25.0.3, build 4debf41", "20.4", ""],
        [
            "Docker version 25.0.3, build 4debf41",
            "26.4",
            "Docker version is not supported: Got 25.0",
        ],
    ],
)
def test_check_docker_version(
    mock_get_command_version, raw_version: str, min_version: str, expected: str
):
    mock_get_command_version(raw_version)
    func = commands.check_docker_version
    assert func(min_version) == expected


@pytest.mark.parametrize(
    "raw_version,versions,expected",
    [
        ["", [], "NodeJS not found."],
        ["", ["16", "17", "18", "19", "20"], "NodeJS not found."],
        ["v20.11.1", ["16", "17", "18", "19", "20"], ""],
        [
            "v22.11.1",
            ["16", "17", "18", "19", "20"],
            "Node version is not supported: Got v22.11.1",
        ],
    ],
)
def test_check_node_version(
    mock_get_command_version, raw_version: str, versions: list[str], expected: str
):
    mock_get_command_version(raw_version)
    func = commands.check_node_version
    assert func(versions) == expected
