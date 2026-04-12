"""Tests for generate."""

from cookiecutter import exceptions as cc_exc
from cookieplone.exceptions import PreFlightException
from cookieplone.exceptions import RepositoryException
from cookieplone.generator import generate
from dataclasses import replace

import pytest


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
    """RepositoryException from get_repository preserves the original message."""
    mock_get_repository.side_effect = RepositoryException("not found")
    config = replace(generate_config, no_input=False)
    with pytest.raises(RepositoryException, match="not found"):
        generate(config)


def test_preflight_exception_reraised(mock_get_repository, generate_config):
    """PreFlightException from get_repository propagates unchanged."""
    mock_get_repository.side_effect = PreFlightException("validation failed")
    config = replace(generate_config, no_input=False)
    with pytest.raises(PreFlightException):
        generate(config)


def test_merges_config_and_repo_global_versions(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_dump_replay,
    mock_write_answers,
    repository_info_with_config,
    generate_config,
    tmp_path,
):
    """generate merges config.global_versions with repo-discovered versions."""
    # Repo-discovered versions (from cookieplone-config.json)
    repo_versions = {"plone.api": "2.1.0", "volto": "18.0.0"}
    repository_info_with_config.global_versions = repo_versions
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.return_value = tmp_path / "output"

    # Caller-provided versions (from parent template)
    caller_versions = {"plone.api": "2.0.0", "plone.restapi": "9.0.0"}
    config = replace(generate_config, no_input=False, global_versions=caller_versions)

    generate(config)

    # generate_state should receive merged versions:
    # caller as base, repo overrides
    call_kwargs = mock_generate_state.call_args
    effective = call_kwargs.kwargs.get("global_versions") or call_kwargs[1].get(
        "global_versions"
    )
    assert effective == {
        "plone.api": "2.1.0",  # repo overrides caller
        "plone.restapi": "9.0.0",  # caller-only key preserved
        "volto": "18.0.0",  # repo-only key preserved
    }
