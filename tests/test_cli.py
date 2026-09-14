from cookieplone import cli
from cookieplone import settings
from cookieplone.exceptions import GeneratorException
from cookieplone.exceptions import RepositoryException
from cookieplone.exceptions import VersionTooOldException
from typer import BadParameter
from typer.testing import CliRunner
from types import SimpleNamespace

import pytest
import typer


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
        assert cli.resolve_tag("") == settings.REPO_DEFAULT_TAG


class TestUsesDefaultRepository:
    """The fallback tag only applies when neither repository nor tag is set."""

    @pytest.fixture(autouse=True)
    def _clear_env(self, monkeypatch):
        monkeypatch.delenv("COOKIEPLONE_REPOSITORY", raising=False)
        monkeypatch.delenv("COOKIEPLONE_REPOSITORY_TAG", raising=False)

    def test_nothing_set(self):
        """With no overrides the run uses the defaults."""
        assert cli.uses_default_repository("") is True

    @pytest.mark.parametrize(
        "env,tag",
        [
            pytest.param(
                {"COOKIEPLONE_REPOSITORY": "gh:org/templates"}, "", id="repository-env"
            ),
            pytest.param({"COOKIEPLONE_REPOSITORY_TAG": "main"}, "", id="tag-env"),
            pytest.param({}, "main", id="tag-option"),
        ],
    )
    def test_any_override(self, monkeypatch, env: dict[str, str], tag: str):
        """Setting the repository or the tag, even to a default value, opts out."""
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        assert cli.uses_default_repository(tag) is False


class TestResolveBaseRepositoryFallback:
    """``resolve_base_repository`` switches to the fallback tag when needed."""

    @pytest.fixture
    def checkouts(self, monkeypatch, tmp_path) -> list[tuple]:
        """Resolve the base repository to ``tmp_path`` and record checkouts."""
        recorded: list[tuple] = []

        def fake_checkout(repo_path, tag, no_input=False):
            recorded.append((repo_path, tag))
            return repo_path

        monkeypatch.setattr(cli, "get_base_repository", lambda *args, **kw: tmp_path)
        monkeypatch.setattr(cli, "checkout_fallback_tag", fake_checkout)
        return recorded

    def test_switches_when_config_missing(self, tmp_path, checkouts):
        """A clone without ``cookieplone-config.json`` moves to the fallback tag."""
        result = cli.resolve_base_repository(
            settings.REPO_DEFAULT, "main", no_input=True, fallback_tag="next"
        )
        assert result == (tmp_path, "next")
        assert checkouts == [(tmp_path, "next")]

    def test_keeps_tag_when_config_present(self, tmp_path, checkouts):
        """A clone that already provides the config stays at the requested tag."""
        (tmp_path / "cookieplone-config.json").write_text("{}")
        result = cli.resolve_base_repository(
            settings.REPO_DEFAULT, "main", no_input=True, fallback_tag="next"
        )
        assert result == (tmp_path, "main")
        assert checkouts == []

    def test_no_fallback_tag(self, tmp_path, checkouts):
        """Without a fallback tag the clone is used as is."""
        result = cli.resolve_base_repository(
            settings.REPO_DEFAULT, "main", no_input=True
        )
        assert result == (tmp_path, "main")
        assert checkouts == []

    def test_checkout_error_becomes_sanity_screen(self, monkeypatch, tmp_path):
        """A failing fallback checkout exits with code 1 via ``sanity_screen``."""
        exception = RepositoryException("could not check out next")
        recorded: list[str] = []

        def fake_checkout(*args, **kwargs):
            raise exception

        monkeypatch.setattr(cli, "get_base_repository", lambda *args, **kw: tmp_path)
        monkeypatch.setattr(cli, "checkout_fallback_tag", fake_checkout)
        monkeypatch.setattr(
            cli.console, "sanity_screen", lambda msg: recorded.append(msg)
        )
        with pytest.raises(typer.Exit) as exc:
            cli.resolve_base_repository(
                settings.REPO_DEFAULT, "main", no_input=True, fallback_tag="next"
            )
        assert exc.value.exit_code == 1
        assert recorded == [exception.message]


class TestCliRepositoryErrorHandling:
    """Repository-resolution errors are surfaced via ``sanity_screen``,
    not as uncaught tracebacks."""

    @pytest.fixture
    def runner(self):
        app = typer.Typer()
        app.command()(cli.cli)
        return app, CliRunner()

    @pytest.fixture
    def recorded_sanity(self, monkeypatch):
        """Capture the message passed to ``console.sanity_screen``."""
        recorded: list[str] = []
        monkeypatch.setattr(
            cli.console, "sanity_screen", lambda msg: recorded.append(msg)
        )
        return recorded

    @pytest.mark.parametrize(
        "exception_factory",
        [
            pytest.param(
                lambda: RepositoryException("could not clone bogus-url"),
                id="repository-exception",
            ),
            pytest.param(
                lambda: VersionTooOldException("cookieplone >= 99.0.0 required"),
                id="version-too-old",
            ),
        ],
    )
    def test_pre_flight_errors_become_sanity_screen(
        self, monkeypatch, runner, recorded_sanity, exception_factory
    ):
        """Pre-flight exceptions exit with code 1 via a single sanity_screen."""
        exception = exception_factory()

        def fake_get_base_repository(*args, **kwargs):
            raise exception

        monkeypatch.setattr(cli, "get_base_repository", fake_get_base_repository)
        app, runner_ = runner

        result = runner_.invoke(app, ["project", "--no-input"])

        assert result.exit_code == 1
        assert recorded_sanity == [exception.message]


class TestCliFallbackTag:
    """``cli`` enables the fallback only for default runs, and generates from
    the tag the repository was checked out at."""

    @pytest.fixture
    def run_cli(self, monkeypatch, tmp_path):
        """Invoke ``cli`` with repository resolution and generation stubbed."""
        monkeypatch.delenv("COOKIEPLONE_REPOSITORY", raising=False)
        monkeypatch.delenv("COOKIEPLONE_REPOSITORY_TAG", raising=False)
        calls: dict = {}

        def fake_resolve(repository, tag, no_input, fallback_tag=""):
            calls["resolve"] = (repository, tag, fallback_tag)
            return tmp_path, fallback_tag or tag

        def fake_generate(config, return_state=False):
            calls["generate"] = config
            raise GeneratorException("stop before rendering")

        template = SimpleNamespace(
            name="project",
            path="templates/project",
            title="Project",
            origin=None,
            underlay=[],
        )
        monkeypatch.setattr(cli, "resolve_base_repository", fake_resolve)
        monkeypatch.setattr(cli, "get_template", lambda *args, **kwargs: template)
        monkeypatch.setattr(cli, "annotate_context", lambda context, **kwargs: context)
        monkeypatch.setattr(cli, "generate", fake_generate)
        monkeypatch.setattr(cli.console, "error", lambda msg: None)
        app = typer.Typer()
        app.command()(cli.cli)

        def func(*args: str) -> dict:
            CliRunner().invoke(
                app, ["project", "--no-input", "--output-dir", str(tmp_path), *args]
            )
            return calls

        return func

    def test_defaults_enable_fallback(self, run_cli):
        """A run without overrides asks for the fallback and generates from it."""
        calls = run_cli()
        assert calls["resolve"] == (
            settings.REPO_DEFAULT,
            settings.REPO_DEFAULT_TAG,
            settings.REPO_FALLBACK_TAG,
        )
        assert calls["generate"].tag == settings.REPO_FALLBACK_TAG

    def test_explicit_tag_disables_fallback(self, run_cli):
        """An explicit ``--tag`` is used as is, even when it names the default."""
        calls = run_cli("--tag", settings.REPO_DEFAULT_TAG)
        assert calls["resolve"] == (
            settings.REPO_DEFAULT,
            settings.REPO_DEFAULT_TAG,
            "",
        )
        assert calls["generate"].tag == settings.REPO_DEFAULT_TAG


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
