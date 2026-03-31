"""Tests for the cookieplone exception-wrapping entry point."""

import pytest
from cookiecutter import exceptions as cc_exc

from cookieplone.exceptions import GeneratorException, OutputDirExistsException
from cookieplone.generator.main import cookieplone


def test_returns_path_on_success(
    mock_cookieplone_inner, state, repository_info, run_config, tmp_path
):
    """cookieplone returns a Path on success."""
    expected = tmp_path / "output"
    mock_cookieplone_inner.return_value = expected
    result = cookieplone(repository_info, state, run_config)
    assert result == expected


def test_wraps_context_decoding_exception(
    mock_cookieplone_inner, state, repository_info, run_config
):
    """ContextDecodingException is wrapped in GeneratorException."""
    mock_cookieplone_inner.side_effect = cc_exc.ContextDecodingException("bad context")
    with pytest.raises(GeneratorException) as exc_info:
        cookieplone(repository_info, state, run_config)
    assert "bad context" in exc_info.value.message


def test_wraps_invalid_mode_exception(
    mock_cookieplone_inner, state, repository_info, run_config
):
    """InvalidModeException is wrapped in GeneratorException."""
    mock_cookieplone_inner.side_effect = cc_exc.InvalidModeException("invalid mode")
    with pytest.raises(GeneratorException):
        cookieplone(repository_info, state, run_config)


def test_wraps_failed_hook_exception(
    mock_cookieplone_inner, state, repository_info, run_config
):
    """FailedHookException is wrapped in GeneratorException."""
    mock_cookieplone_inner.side_effect = cc_exc.FailedHookException("hook failed")
    with pytest.raises(GeneratorException):
        cookieplone(repository_info, state, run_config)


def test_wraps_unknown_extension(
    mock_cookieplone_inner, state, repository_info, run_config
):
    """UnknownExtension is wrapped in GeneratorException."""
    mock_cookieplone_inner.side_effect = cc_exc.UnknownExtension("unknown ext")
    with pytest.raises(GeneratorException):
        cookieplone(repository_info, state, run_config)


def test_wraps_output_dir_exists(
    mock_cookieplone_inner, state, repository_info, run_config, tmp_path
):
    """OutputDirExistsException from cookiecutter is wrapped."""
    mock_cookieplone_inner.side_effect = cc_exc.OutputDirExistsException(str(tmp_path))
    with pytest.raises(OutputDirExistsException):
        cookieplone(repository_info, state, run_config)


def test_wraps_undefined_variable(
    mock_cookieplone_inner, state, repository_info, run_config
):
    """UndefinedVariableInTemplate is wrapped in GeneratorException."""
    err = cc_exc.UndefinedVariableInTemplate("undefined var", ValueError("orig"), {})
    mock_cookieplone_inner.side_effect = err
    with pytest.raises(GeneratorException) as exc_info:
        cookieplone(repository_info, state, run_config)
    assert "Undefined variable" in exc_info.value.message


def test_preserves_state_on_exception(
    mock_cookieplone_inner, state, repository_info, run_config
):
    """GeneratorException carries the CookieploneState."""
    mock_cookieplone_inner.side_effect = cc_exc.ContextDecodingException("fail")
    with pytest.raises(GeneratorException) as exc_info:
        cookieplone(repository_info, state, run_config)
    assert exc_info.value.state is state


def test_undefined_variable_wrapping_output_dir_exists(
    mock_cookieplone_inner, state, repository_info, run_config, tmp_path
):
    """UndefinedVariableInTemplate wrapping OutputDirExistsException."""
    inner_exc = cc_exc.OutputDirExistsException(str(tmp_path))
    err = cc_exc.UndefinedVariableInTemplate("undefined var", inner_exc, {})
    mock_cookieplone_inner.side_effect = err
    with pytest.raises(OutputDirExistsException):
        cookieplone(repository_info, state, run_config)


def test_cleanup_paths_called(
    mock_cookieplone_inner, state, repository_info, run_config, tmp_path
):
    """Cleanup paths are removed after successful generation."""
    cleanup_dir = tmp_path / "to_clean"
    cleanup_dir.mkdir()
    repository_info.cleanup_paths = [cleanup_dir]
    mock_cookieplone_inner.return_value = tmp_path / "output"
    cookieplone(repository_info, state, run_config)
    assert not cleanup_dir.exists()
