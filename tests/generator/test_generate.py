"""Tests for generate."""

from dataclasses import replace

import pytest
from cookiecutter import exceptions as cc_exc

from cookieplone.exceptions import PreFlightException, RepositoryException
from cookieplone.generator import generate


def test_replay_with_no_input_raises(generate_config):
    """generate raises InvalidModeException when replay + no_input."""
    config = replace(generate_config, replay=True, no_input=True)
    with pytest.raises(cc_exc.InvalidModeException):
        generate(config)


def test_replay_with_extra_context_raises(generate_config):
    """generate raises InvalidModeException when replay + extra_context."""
    config = replace(
        generate_config,
        replay=True,
        no_input=False,
        extra_context={"key": "val"},
    )
    with pytest.raises(cc_exc.InvalidModeException):
        generate(config)


def test_repository_exception_reraised(mock_get_repository, generate_config):
    """RepositoryException from get_repository is re-raised."""
    mock_get_repository.side_effect = RepositoryException("not found")
    config = replace(generate_config, no_input=False)
    with pytest.raises(RepositoryException):
        generate(config)


def test_preflight_exception_reraised(mock_get_repository, generate_config):
    """PreFlightException from get_repository propagates unchanged."""
    mock_get_repository.side_effect = PreFlightException("validation failed")
    config = replace(generate_config, no_input=False)
    with pytest.raises(PreFlightException):
        generate(config)
