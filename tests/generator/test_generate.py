"""Tests for generate."""

import pytest
from cookiecutter import exceptions as cc_exc

from cookieplone.exceptions import PreFlightException, RepositoryException
from cookieplone.generator import generate


def test_replay_with_no_input_raises(tmp_path):
    """generate raises InvalidModeException when replay + no_input."""
    with pytest.raises(cc_exc.InvalidModeException):
        generate(
            repository="some-repo",
            tag="",
            no_input=True,
            extra_context=None,
            replay=True,
            overwrite_if_exists=False,
            output_dir=tmp_path,
            config_file=None,
            default_config=None,
            passwd=None,
            template_path=None,
            skip_if_file_exists=False,
            keep_project_on_failure=False,
            template_name="test",
        )


def test_replay_with_extra_context_raises(tmp_path):
    """generate raises InvalidModeException when replay + extra_context."""
    with pytest.raises(cc_exc.InvalidModeException):
        generate(
            repository="some-repo",
            tag="",
            no_input=False,
            extra_context={"key": "val"},
            replay=True,
            overwrite_if_exists=False,
            output_dir=tmp_path,
            config_file=None,
            default_config=None,
            passwd=None,
            template_path=None,
            skip_if_file_exists=False,
            keep_project_on_failure=False,
            template_name="test",
        )


def test_repository_exception_reraised(mock_get_repository, tmp_path):
    """RepositoryException from get_repository is re-raised."""
    mock_get_repository.side_effect = RepositoryException("not found")
    with pytest.raises(RepositoryException):
        generate(
            repository="some-repo",
            tag="",
            no_input=False,
            extra_context=None,
            replay=False,
            overwrite_if_exists=False,
            output_dir=tmp_path,
            config_file=None,
            default_config=None,
            passwd=None,
            template_path=None,
            skip_if_file_exists=False,
            keep_project_on_failure=False,
            template_name="test",
        )


def test_preflight_exception_reraised(mock_get_repository, tmp_path):
    """PreFlightException from get_repository propagates unchanged."""
    mock_get_repository.side_effect = PreFlightException("validation failed")
    with pytest.raises(PreFlightException):
        generate(
            repository="some-repo",
            tag="",
            no_input=False,
            extra_context=None,
            replay=False,
            overwrite_if_exists=False,
            output_dir=tmp_path,
            config_file=None,
            default_config=None,
            passwd=None,
            template_path=None,
            skip_if_file_exists=False,
            keep_project_on_failure=False,
            template_name="test",
        )
