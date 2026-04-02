"""Tests for cookieplone.utils.cookiecutter."""

import json
import sys

import pytest
from cookiecutter.exceptions import OutputDirExistsException
from jinja2 import Environment
from jinja2.exceptions import UndefinedError

from cookieplone.utils.cookiecutter import (
    create_jinja_env,
    dump_replay,
    import_patch,
    load_replay,
    parse_output_dir_exception,
    parse_undefined_error,
)


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


class TestImportPatch:
    """Tests for import_patch."""

    def test_adds_repo_dir_to_sys_path(self, tmp_path):
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()
        with import_patch(repo_dir):
            assert str(repo_dir) in sys.path

    def test_restores_sys_path_on_exit(self, tmp_path):
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()
        original_path = sys.path.copy()
        with import_patch(repo_dir):
            pass
        assert sys.path == original_path

    def test_restores_sys_path_on_exception(self, tmp_path):
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()
        original_path = sys.path.copy()
        with pytest.raises(RuntimeError), import_patch(repo_dir):
            raise RuntimeError("boom")
        assert sys.path == original_path

    def test_accepts_string_path(self, tmp_path):
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()
        with import_patch(str(repo_dir)):
            assert str(repo_dir) in sys.path


class TestLoadReplay:
    """Tests for load_replay."""

    def test_returns_empty_dict_when_replay_is_false(self, tmp_path):
        result = load_replay(tmp_path, tmp_path, False, "template")
        assert result == {}

    def test_loads_from_replay_dir_when_replay_is_true(self, tmp_path):
        replay_dir = tmp_path / "replay"
        replay_dir.mkdir()
        context = {"cookiecutter": {"name": "test"}}
        replay_file = replay_dir / "mytemplate.json"
        replay_file.write_text(json.dumps(context))
        result = load_replay(tmp_path, replay_dir, True, "mytemplate")
        assert result == context

    def test_loads_from_explicit_path(self, tmp_path):
        context = {"cookiecutter": {"name": "test"}}
        replay_file = tmp_path / "custom.json"
        replay_file.write_text(json.dumps(context))
        result = load_replay(tmp_path, tmp_path, replay_file, "ignored")
        assert result == context


class TestDumpReplay:
    """Tests for dump_replay."""

    def test_dump_creates_replay_file(self, tmp_path):
        from cookieplone.config import Answers

        answers = Answers(answers={"name": "test-project"})
        dump_replay(answers, tmp_path, "mytemplate")
        replay_file = tmp_path / "mytemplate.json"
        assert replay_file.exists()
        data = json.loads(replay_file.read_text())
        assert data["cookiecutter"] == {"name": "test-project"}


class TestParseUndefinedError:
    """Tests for parse_undefined_error."""

    @pytest.mark.parametrize(
        ("error_msg", "base_msg", "expected"),
        [
            (
                "'dict object' has no attribute '__cookieplone_template'",
                "Error",
                "Error: Variable '__cookieplone_template' is undefined",
            ),
            (
                "'dict object' has no attribute 'my_var'",
                "",
                ": Variable 'my_var' is undefined",
            ),
            (
                "something weird !!!",
                "Error",
                "Error",
            ),
        ],
        ids=["typical_error", "empty_base_msg", "non_identifier"],
    )
    def test_parse_undefined_error(self, error_msg, base_msg, expected):
        exc = UndefinedError(error_msg)
        result = parse_undefined_error(exc, base_msg)
        assert result == expected

    def test_empty_message(self):
        exc = UndefinedError("")
        result = parse_undefined_error(exc, "base")
        assert result == "base"
