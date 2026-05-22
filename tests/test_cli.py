from click.exceptions import BadParameter
from cookieplone import cli

import pytest


@pytest.mark.parametrize(
    "value,answers_data,expected",
    [
        ([], {}, {}),
        (
            ["foo=bar", "bar=bar"],
            {},
            {"foo": "bar", "bar": "bar"},
        ),  # Only extra context
        (["foo=1", "bar=2"], {}, {"foo": "1", "bar": "2"}),
        (
            ["foo=1", "bar=2"],
            {"bar": "3"},
            {"foo": "1", "bar": "2"},
        ),  # Extra context has priority over answers_data
        (
            [],
            {"bar": "3"},
            {"bar": "3"},
        ),  # Only answers_data
        (["foo=1", "bar=2"], {"foobar": "3"}, {"foo": "1", "bar": "2", "foobar": "3"}),
    ],
)
def test_parse_extra_context(value: list[str], answers_data: dict, expected: dict):
    func = cli.parse_extra_context
    assert func(value, answers_data) == expected


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
    "env_var,value,expected",
    (
        ("FOO", "bar", ""),
        ("COOKIEPLONE_REPO_PASSWORD", "bar", "bar"),
        ("COOKIECUTTER_REPO_PASSWORD", "foo", "foo"),
    ),
)
def test_get_password_from_env(monkeypatch, env_var: str, value: str, expected: str):
    """Test get_password_from_env."""
    monkeypatch.setenv(env_var, value)
    func = cli.get_password_from_env
    result = func()
    assert result == expected


class TestResolveTag:
    """Precedence: CLI ``--tag`` > ``COOKIEPLONE_REPOSITORY_TAG`` > default."""

    @pytest.fixture(autouse=True)
    def _clear_env(self, monkeypatch):
        monkeypatch.delenv("COOKIEPLONE_REPOSITORY_TAG", raising=False)

    def test_cli_value_wins_over_env(self, monkeypatch):
        """An explicit CLI ``--tag`` beats the environment variable."""
        monkeypatch.setenv("COOKIEPLONE_REPOSITORY_TAG", "from-env")
        assert cli.resolve_tag("from-cli") == "from-cli"

    def test_env_used_when_cli_empty(self, monkeypatch):
        """The env variable is consulted when no CLI value is provided."""
        monkeypatch.setenv("COOKIEPLONE_REPOSITORY_TAG", "from-env")
        assert cli.resolve_tag("") == "from-env"

    def test_default_when_neither_set(self):
        """Falls back to ``settings.REPO_DEFAULT_TAG`` when nothing is set."""
        from cookieplone import settings

        assert cli.resolve_tag("") == settings.REPO_DEFAULT_TAG


@pytest.mark.parametrize(
    "template,extra_context,expected",
    [
        ("", [], ("", [])),
        ("project", [], ("project", [])),
        (
            "project",
            ["project_slug=foo", "title=FooBar"],
            ("project", ["project_slug=foo", "title=FooBar"]),
        ),
        (
            "",
            ["project_slug=foo", "title=FooBar"],
            ("", ["project_slug=foo", "title=FooBar"]),
        ),
        (
            "project_slug=foo",
            ["title=FooBar"],
            ("", ["project_slug=foo", "title=FooBar"]),
        ),
    ],
)
def test_parse_arguments(
    template: str, extra_context: list[str] | None, expected: tuple[str, list[str]]
):
    func = cli.parse_arguments
    results = func(template, extra_context)
    assert results == expected
