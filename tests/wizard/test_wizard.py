"""Tests for the wizard function."""

from unittest.mock import MagicMock

from cookieplone.config.state import Answers
from cookieplone.wizard import wizard


def test_returns_answers(mock_create_form, mock_get_renderer, state):
    """wizard returns an Answers instance."""
    mock_form = MagicMock()
    mock_form.user_answers = {"title": "My Project"}
    mock_create_form.return_value = mock_form
    mock_renderer_instance = MagicMock()
    mock_renderer_instance.render.return_value = {
        "cookiecutter": {"title": "My Project"}
    }
    mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    result = wizard(state, base_answers={}, no_input=True, root_key="cookiecutter")
    assert isinstance(result, Answers)
    assert result.answers == {"title": "My Project"}


def test_no_input_uses_noinput_renderer(mock_create_form, mock_get_renderer, state):
    """wizard uses 'noinput' renderer when no_input=True."""
    mock_form = MagicMock()
    mock_form.user_answers = {}
    mock_create_form.return_value = mock_form
    mock_renderer_instance = MagicMock()
    mock_renderer_instance.render.return_value = {"cookiecutter": {}}
    mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    wizard(state, base_answers={}, no_input=True, root_key="cookiecutter")
    mock_get_renderer.assert_called_once_with("noinput")


def test_interactive_uses_cookiecutter_renderer(
    mock_create_form, mock_get_renderer, state
):
    """wizard uses 'cookiecutter' renderer when no_input=False."""
    mock_form = MagicMock()
    mock_form.user_answers = {}
    mock_create_form.return_value = mock_form
    mock_renderer_instance = MagicMock()
    mock_renderer_instance.render.return_value = {"cookiecutter": {}}
    mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    wizard(state, base_answers={}, no_input=False, root_key="cookiecutter")
    mock_get_renderer.assert_called_once_with("cookiecutter")


def test_render_called_with_confirm_false_for_no_input(
    mock_create_form, mock_get_renderer, state
):
    """render is called with confirm=False when no_input=True."""
    mock_form = MagicMock()
    mock_form.user_answers = {}
    mock_create_form.return_value = mock_form
    mock_renderer_instance = MagicMock()
    mock_renderer_instance.render.return_value = {"cookiecutter": {}}
    mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    wizard(state, base_answers={}, no_input=True, root_key="cookiecutter")
    mock_renderer_instance.render.assert_called_once_with(
        initial_answers={}, confirm=False
    )


def test_render_called_with_confirm_true_for_interactive(
    mock_create_form, mock_get_renderer, state
):
    """render is called with confirm=True when no_input=False."""
    mock_form = MagicMock()
    mock_form.user_answers = {}
    mock_create_form.return_value = mock_form
    mock_renderer_instance = MagicMock()
    mock_renderer_instance.render.return_value = {"cookiecutter": {}}
    mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    wizard(state, base_answers={}, no_input=False, root_key="cookiecutter")
    mock_renderer_instance.render.assert_called_once_with(
        initial_answers={}, confirm=True
    )


def test_user_answers_stored(mock_create_form, mock_get_renderer, state):
    """wizard stores user_answers from the form on the state."""
    mock_form = MagicMock()
    mock_form.user_answers = {"title": "User Value"}
    mock_create_form.return_value = mock_form
    mock_renderer_instance = MagicMock()
    mock_renderer_instance.render.return_value = {
        "cookiecutter": {"title": "User Value"}
    }
    mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    result = wizard(state, base_answers={}, no_input=True, root_key="cookiecutter")
    assert result.user_answers == {"title": "User Value"}
