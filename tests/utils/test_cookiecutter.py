"""Tests for cookieplone.utils.cookiecutter."""

import pytest
from cookiecutter.exceptions import OutputDirExistsException
from jinja2 import Environment

from cookieplone.utils.cookiecutter import create_jinja_env, parse_output_dir_exception


class TestParseOutputDirException:
    """Tests for parse_output_dir_exception."""

    @pytest.fixture
    def project_dir(self, tmp_path):
        path = tmp_path / "my-project"
        path.mkdir()
        return path

    @pytest.mark.parametrize(
        ("msg_template", "expect_path"),
        [
            ("{path}", True),
            ('"{path}" already exists', True),
            ("some unknown error", False),
            ("/nonexistent/path/abc123", False),
        ],
        ids=[
            "plain_path",
            "path_in_sentence",
            "no_path",
            "nonexistent_path",
        ],
    )
    def test_parse_output_dir_exception(self, project_dir, msg_template, expect_path):
        msg = msg_template.format(path=project_dir)
        exc = OutputDirExistsException(msg)
        result = parse_output_dir_exception(exc)
        if expect_path:
            assert result == f"'{project_dir}'"
        else:
            assert result == ""


class TestCreateJinjaEnv:
    """Tests for create_jinja_env."""

    def test_returns_environment(self):
        """create_jinja_env returns a Jinja2 Environment."""
        env = create_jinja_env({})
        assert isinstance(env, Environment)

    def test_wraps_plain_dict(self):
        """A plain data dict is wrapped under DEFAULT_DATA_KEY."""
        env = create_jinja_env({"title": "Hello"})
        result = env.from_string("{{ cookiecutter.title }}").render()
        assert result == "Hello"

    def test_accepts_full_context(self):
        """A dict already keyed by DEFAULT_DATA_KEY is used as-is."""
        context = {"cookiecutter": {"title": "Hello"}}
        env = create_jinja_env(context)
        result = env.from_string("{{ cookiecutter.title }}").render()
        assert result == "Hello"

    def test_renders_expression(self):
        """Jinja2 expressions are evaluated against the context."""
        env = create_jinja_env({"name": "plone", "version": "6.1"})
        template = "{{ cookiecutter.name }}-{{ cookiecutter.version }}"
        assert env.from_string(template).render() == "plone-6.1"

    def test_env_is_reusable(self):
        """A single env can render multiple templates."""
        env = create_jinja_env({"a": "1", "b": "2"})
        assert env.from_string("{{ cookiecutter.a }}").render() == "1"
        assert env.from_string("{{ cookiecutter.b }}").render() == "2"
