from unittest.mock import patch

import pytest
import typer
from click.exceptions import BadParameter
from cookiecutter.exceptions import RepositoryCloneFailed, RepositoryNotFound

from cookieplone import cli


@pytest.mark.parametrize(
    "value,expected",
    [
        ([], {}),
        (["foo=bar", "bar=bar"], {"foo": "bar", "bar": "bar"}),
        (["foo=1", "bar=2"], {"foo": "1", "bar": "2"}),
    ],
)
def test_parse_extra_context(value: list[str], expected: dict):
    func = cli.parse_extra_context
    assert func(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, []),
        ([], []),
        (["foo=bar", "bar=bar"], ["foo=bar", "bar=bar"]),
        (["foo=1", "bar=2"], ["foo=1", "bar=2"]),
    ],
)
def test_validate_extra_context_pass(value: list[str] | None, expected: list):
    func = cli.validate_extra_context
    assert func(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (["foo=bar", "bar2"], "bar2"),
        (["foo-1", "bar=2"], "foo-1"),
    ],
)
def test_validate_extra_context_fail(value: list[str] | None, expected: str):
    func = cli.validate_extra_context
    with pytest.raises(BadParameter) as exc:
        func(value)
    assert expected in str(exc)


@pytest.mark.parametrize(
    "exception",
    [
        RepositoryNotFound("No cookiecutter.json found"),
        RepositoryCloneFailed("The foo branch of repository bar could not found"),
    ],
)
@patch("cookieplone.cli.console.error_screen")
@patch("cookieplone.cli.get_base_repository")
def test_cli_repository_error_screen(
    mock_get_base_repository, mock_error_screen, exception: Exception
):
    """Repository failures display an error screen and exit with status 1."""
    mock_get_base_repository.side_effect = exception
    with pytest.raises(typer.Exit) as exc:
        cli.cli()
    assert exc.value.exit_code == 1
    mock_error_screen.assert_called_once()
