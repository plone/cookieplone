"""Tests for cookieplone.utils.cookiecutter."""

import pytest
from cookiecutter.exceptions import OutputDirExistsException

from cookieplone.utils.cookiecutter import parse_output_dir_exception


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
