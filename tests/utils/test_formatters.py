from cookieplone.utils import formatters
from unittest.mock import patch

import pytest
import subprocess


class TestUvx:
    """Tests for the _uvx helper."""

    @patch("cookieplone.utils.formatters.subprocess.run")
    def test_calls_uvx_with_tool_and_args(self, mock_run, tmp_path):
        formatters._uvx("ruff", ["check", "--fix"], tmp_path)
        mock_run.assert_called_once_with(
            ["uvx", "ruff", "check", "--fix"],
            capture_output=True,
            check=True,
            cwd=tmp_path,
        )

    @patch("cookieplone.utils.formatters.subprocess.run")
    def test_calls_uvx_with_no_extra_args(self, mock_run, tmp_path):
        formatters._uvx("black", [], tmp_path)
        mock_run.assert_called_once_with(
            ["uvx", "black"],
            capture_output=True,
            check=True,
            cwd=tmp_path,
        )

    @patch("cookieplone.utils.formatters.subprocess.run")
    def test_places_from_spec_before_tool(self, mock_run, tmp_path):
        formatters._uvx("zpretty", ["-i", "a.zcml"], tmp_path, from_="zpretty>=5.0.0")
        mock_run.assert_called_once_with(
            ["uvx", "--from", "zpretty>=5.0.0", "zpretty", "-i", "a.zcml"],
            capture_output=True,
            check=True,
            cwd=tmp_path,
        )

    @patch("cookieplone.utils.formatters.subprocess.run")
    def test_places_python_spec_before_from_spec(self, mock_run, tmp_path):
        formatters._uvx(
            "zpretty",
            ["-i", "a.zcml"],
            tmp_path,
            from_="zpretty>=5.0.0",
            python=">=3.11",
        )
        mock_run.assert_called_once_with(
            [
                "uvx",
                "--python",
                ">=3.11",
                "--from",
                "zpretty>=5.0.0",
                "zpretty",
                "-i",
                "a.zcml",
            ],
            capture_output=True,
            check=True,
            cwd=tmp_path,
        )

    @patch(
        "cookieplone.utils.formatters.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "uvx"),
    )
    def test_propagates_subprocess_error(self, mock_run, tmp_path):
        with pytest.raises(subprocess.CalledProcessError):
            formatters._uvx("ruff", ["check"], tmp_path)


class TestRunZpretty:
    """Tests for run_zpretty."""

    @patch("cookieplone.utils.formatters._uvx")
    def test_skips_when_no_src_dir(self, mock_uvx, tmp_path):
        formatters.run_zpretty(tmp_path)
        mock_uvx.assert_not_called()

    @patch("cookieplone.utils.formatters._uvx")
    def test_skips_when_no_xml_files(self, mock_uvx, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "module.py").write_text("# python")
        formatters.run_zpretty(tmp_path)
        mock_uvx.assert_not_called()

    @patch("cookieplone.utils.formatters._uvx")
    def test_calls_zpretty_with_xml_and_zcml_files(self, mock_uvx, dummy_package):
        formatters.run_zpretty(dummy_package)
        mock_uvx.assert_called_once()
        args = mock_uvx.call_args
        assert args[0][0] == "zpretty"
        cli_args = args[0][1]
        assert "-i" in cli_args
        # Should include .xml and .zcml files
        file_args = [a for a in cli_args if a != "-i"]
        extensions = {f.rsplit(".", 1)[-1] for f in file_args}
        assert extensions <= {"xml", "zcml"}
        assert len(file_args) == 3  # configure.zcml, metadata.xml, rolemap.xml
        assert args[1]["from_"] == formatters.ZPRETTY_REQUIREMENT
        assert args[1]["python"] == formatters.ZPRETTY_PYTHON

    @patch("cookieplone.utils.formatters.subprocess.run")
    def test_zpretty_command_requires_zpretty_5(self, mock_run, dummy_package):
        formatters.run_zpretty(dummy_package)
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "uvx"
        assert cmd.index("--from") < cmd.index("zpretty")
        assert cmd[cmd.index("--from") + 1] == "zpretty>=5.0.0"

    @patch("cookieplone.utils.formatters.subprocess.run")
    def test_zpretty_command_runs_on_python_3_11_or_newer(
        self, mock_run, dummy_package
    ):
        formatters.run_zpretty(dummy_package)
        cmd = mock_run.call_args[0][0]
        assert cmd.index("--python") < cmd.index("zpretty")
        assert cmd[cmd.index("--python") + 1] == ">=3.11"


class TestRunIsort:
    """Tests for run_isort."""

    @patch("cookieplone.utils.formatters._uvx")
    def test_calls_isort_with_settings(self, mock_uvx, dummy_package):
        formatters.run_isort(dummy_package)
        mock_uvx.assert_called_once()
        args = mock_uvx.call_args[0]
        assert args[0] == "isort"
        cli_args = args[1]
        assert "--quiet" in cli_args
        assert "--settings" in cli_args
        assert str(dummy_package / "pyproject.toml") in cli_args
        assert str(dummy_package) in cli_args


class TestRunBlack:
    """Tests for run_black."""

    @patch("cookieplone.utils.formatters._uvx")
    def test_calls_black_with_config(self, mock_uvx, dummy_package):
        formatters.run_black(dummy_package)
        mock_uvx.assert_called_once()
        args = mock_uvx.call_args[0]
        assert args[0] == "black"
        cli_args = args[1]
        assert "--quiet" in cli_args
        assert "--config" in cli_args
        assert str(dummy_package / "pyproject.toml") in cli_args
        assert str(dummy_package) in cli_args


class TestRunRuff:
    """Tests for run_ruff."""

    @patch("cookieplone.utils.formatters._uvx")
    def test_calls_ruff_check_and_format(self, mock_uvx, dummy_package):
        formatters.run_ruff(dummy_package)
        assert mock_uvx.call_count == 2
        # First call: ruff check --select I --fix
        check_args = mock_uvx.call_args_list[0][0]
        assert check_args[0] == "ruff"
        assert "check" in check_args[1]
        assert "--select" in check_args[1]
        assert "I" in check_args[1]
        assert "--fix" in check_args[1]
        assert "--config" in check_args[1]
        # Second call: ruff format
        format_args = mock_uvx.call_args_list[1][0]
        assert format_args[0] == "ruff"
        assert "format" in format_args[1]
        assert "--config" in format_args[1]
