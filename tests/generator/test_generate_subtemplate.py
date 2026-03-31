"""Tests for generate_subtemplate."""

from collections import OrderedDict

import pytest

from cookieplone.config.state import CookieploneState
from cookieplone.exceptions import GeneratorException
from cookieplone.generator import generate_subtemplate


def test_enables_quiet_mode(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    tmp_path,
):
    """generate_subtemplate enables quiet mode."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    mock_generate.return_value = tmp_path / "output"
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    generate_subtemplate(
        template_path="sub",
        output_dir=tmp_path,
        folder_name="my_folder",
        context=context,
    )
    mock_console.enable_quiet_mode.assert_called_once()


def test_disables_quiet_mode_on_success(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    tmp_path,
):
    """generate_subtemplate disables quiet mode after success."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    mock_generate.return_value = tmp_path / "output"
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    generate_subtemplate(
        template_path="sub",
        output_dir=tmp_path,
        folder_name="my_folder",
        context=context,
    )
    mock_console.disable_quiet_mode.assert_called_once()


def test_disables_quiet_mode_on_failure(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    tmp_path,
):
    """generate_subtemplate disables quiet mode even on failure."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    state = CookieploneState(
        schema={}, data={"cookiecutter": {}}, root_key="cookiecutter"
    )
    mock_generate.side_effect = GeneratorException(
        message="fail", state=state, original=None
    )
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    with pytest.raises(GeneratorException):
        generate_subtemplate(
            template_path="sub",
            output_dir=tmp_path,
            folder_name="my_folder",
            context=context,
        )
    mock_console.disable_quiet_mode.assert_called_once()


def test_calls_generate_with_no_input(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    tmp_path,
):
    """generate_subtemplate always passes no_input=True."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    mock_generate.return_value = tmp_path / "output"
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    generate_subtemplate(
        template_path="sub",
        output_dir=tmp_path,
        folder_name="my_folder",
        context=context,
    )
    call_kwargs = mock_generate.call_args
    # no_input is the 3rd positional arg (index 2)
    assert call_kwargs[0][2] is True


def test_sets_folder_name_in_extra_context(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    tmp_path,
):
    """generate_subtemplate sets __folder_name in extra_context."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    mock_generate.return_value = tmp_path / "output"
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    generate_subtemplate(
        template_path="sub",
        output_dir=tmp_path,
        folder_name="my_folder",
        context=context,
    )
    call_args = mock_generate.call_args[0]
    # extra_context is the 4th positional arg (index 3)
    assert call_args[3]["__folder_name"] == "my_folder"


def test_removes_files_when_specified(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    mock_remove_files,
    tmp_path,
):
    """generate_subtemplate calls remove_files when specified."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    output = tmp_path / "output"
    output.mkdir()
    mock_generate.return_value = output
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    generate_subtemplate(
        template_path="sub",
        output_dir=tmp_path,
        folder_name="my_folder",
        context=context,
        remove_files=["README.md"],
    )
    mock_remove_files.assert_called_once_with(output, ["README.md"])


def test_returns_path(
    mock_remove_internal_keys,
    mock_get_repository_root,
    mock_console,
    mock_generate,
    tmp_path,
):
    """generate_subtemplate returns the generated path."""
    mock_remove_internal_keys.return_value = {"title": "Test"}
    mock_get_repository_root.return_value = str(tmp_path / "repo")
    expected = tmp_path / "output"
    mock_generate.return_value = expected
    context = OrderedDict({"title": "Test", "_template": "/some/path"})

    result = generate_subtemplate(
        template_path="sub",
        output_dir=tmp_path,
        folder_name="my_folder",
        context=context,
    )
    assert result == expected
