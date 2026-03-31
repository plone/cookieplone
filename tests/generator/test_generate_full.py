"""Tests for the generate() happy path and exception handling in __init__.py."""

from unittest.mock import MagicMock

import pytest
from cookiecutter import exceptions as cc_exc

from cookieplone.exceptions import GeneratorException
from cookieplone.generator import generate
from cookieplone.settings import COOKIEPLONE_ANSWERS_FILE


def test_happy_path_returns_path(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    tmp_path,
):
    """generate returns the generated project path on success."""
    expected = tmp_path / "output"
    expected.mkdir()
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.return_value = expected
    mock_write_answers.return_value = tmp_path / "answers.json"
    mock_write_answers.return_value.touch()

    result = generate(
        repository="gh:plone/cookieplone-templates",
        tag="",
        no_input=True,
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
        template_name="project",
    )
    assert result == expected


def test_dumps_answers_on_success(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    tmp_path,
):
    """generate calls _dump_answers and dump_replay in the finally block."""
    expected = tmp_path / "output"
    expected.mkdir()
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.return_value = expected
    answers_path = tmp_path / "answers.json"
    answers_path.touch()
    mock_write_answers.return_value = answers_path

    generate(
        repository="gh:plone/cookieplone-templates",
        tag="",
        no_input=True,
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
        template_name="project",
    )
    mock_write_answers.assert_called_once()
    mock_dump_replay.assert_called_once()


def test_moves_answers_file_to_output(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    tmp_path,
):
    """generate moves the answers file into the generated output directory."""
    output = tmp_path / "output"
    output.mkdir()
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.return_value = output
    answers_path = tmp_path / "answers.json"
    answers_path.write_text("{}")
    mock_write_answers.return_value = answers_path

    generate(
        repository="gh:plone/cookieplone-templates",
        tag="",
        no_input=True,
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
        template_name="project",
    )
    assert (output / COOKIEPLONE_ANSWERS_FILE).exists()
    assert not answers_path.exists()


def test_skips_dump_when_disabled(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    tmp_path,
):
    """generate skips dumping answers when dump_answers=False."""
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.return_value = tmp_path / "output"

    generate(
        repository="gh:plone/cookieplone-templates",
        tag="",
        no_input=True,
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
        template_name="project",
        dump_answers=False,
    )
    mock_write_answers.assert_not_called()
    mock_dump_replay.assert_not_called()


def test_wraps_undefined_variable(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    tmp_path,
):
    """generate wraps UndefinedVariableInTemplate in GeneratorException."""
    mock_get_repository.return_value = repository_info_with_config
    inner_error = MagicMock()
    inner_error.message = "original error"
    err = cc_exc.UndefinedVariableInTemplate(
        "undefined var", inner_error, {"key": "val"}
    )
    mock_cookieplone_entry.side_effect = err
    mock_write_answers.return_value = tmp_path / "answers.json"

    with pytest.raises(GeneratorException) as exc_info:
        generate(
            repository="gh:plone/cookieplone-templates",
            tag="",
            no_input=True,
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
            template_name="project",
            dump_answers=False,
        )
    assert "undefined var" in exc_info.value.message


def test_wraps_generic_exception(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    tmp_path,
):
    """generate wraps unexpected exceptions in GeneratorException."""
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.side_effect = RuntimeError("unexpected")
    mock_write_answers.return_value = tmp_path / "answers.json"

    with pytest.raises(GeneratorException) as exc_info:
        generate(
            repository="gh:plone/cookieplone-templates",
            tag="",
            no_input=True,
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
            template_name="project",
            dump_answers=False,
        )
    assert "unexpected" in exc_info.value.message


def test_generator_exception_propagates(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    state,
    tmp_path,
):
    """generate re-raises GeneratorException as-is."""
    mock_get_repository.return_value = repository_info_with_config
    original = GeneratorException(message="gen fail", state=state, original=None)
    mock_cookieplone_entry.side_effect = original
    mock_write_answers.return_value = tmp_path / "answers.json"

    with pytest.raises(GeneratorException) as exc_info:
        generate(
            repository="gh:plone/cookieplone-templates",
            tag="",
            no_input=True,
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
            template_name="project",
            dump_answers=False,
        )
    assert exc_info.value is original


def test_dumps_answers_without_move_on_failure(
    mock_get_repository,
    mock_load_replay,
    mock_generate_state,
    mock_cookieplone_entry,
    mock_write_answers,
    mock_dump_replay,
    repository_info_with_config,
    state,
    tmp_path,
):
    """generate still dumps answers on failure but does not move the file."""
    mock_get_repository.return_value = repository_info_with_config
    mock_cookieplone_entry.side_effect = GeneratorException(
        message="fail", state=state, original=None
    )
    answers_path = tmp_path / "answers.json"
    answers_path.write_text("{}")
    mock_write_answers.return_value = answers_path

    with pytest.raises(GeneratorException):
        generate(
            repository="gh:plone/cookieplone-templates",
            tag="",
            no_input=True,
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
            template_name="project",
        )
    mock_write_answers.assert_called_once()
    mock_dump_replay.assert_called_once()
    # File was NOT moved (no dump_location since generation failed)
    assert answers_path.exists()


def test_failed_hook_reraised_as_repository_exception(
    mock_get_repository,
    mock_load_replay,
    tmp_path,
):
    """FailedHookException from get_repository is wrapped in RepositoryException."""
    from cookieplone.exceptions import FailedHookException, RepositoryException

    mock_get_repository.side_effect = FailedHookException("hook fail")
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
