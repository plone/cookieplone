"""Tests for the wizard function."""

from cookieplone.config.state import Answers
from cookieplone.exceptions import InvalidConfiguration
from cookieplone.settings import RENDERER_VAR
from cookieplone.wizard import _resolve_renderer
from cookieplone.wizard import wizard
from unittest.mock import MagicMock

import pytest


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


class TestResolveRenderer:
    """Tests for the renderer resolution helper."""

    def test_no_input_always_wins(self, monkeypatch):
        """no_input=True forces noinput regardless of other inputs."""
        monkeypatch.setenv(RENDERER_VAR, "rich")
        assert _resolve_renderer(no_input=True, renderer="stdlib") == "noinput"

    def test_default_when_nothing_configured(self, monkeypatch):
        """Falls back to DEFAULT_RENDERER when nothing is configured."""
        monkeypatch.delenv(RENDERER_VAR, raising=False)
        assert _resolve_renderer(no_input=False) == "cookiecutter"

    def test_explicit_renderer_arg(self, monkeypatch):
        """Explicit renderer argument is honoured when env var is unset."""
        monkeypatch.delenv(RENDERER_VAR, raising=False)
        assert _resolve_renderer(no_input=False, renderer="rich") == "rich"

    def test_env_var_overrides_arg(self, monkeypatch):
        """COOKIEPLONE_RENDERER env var takes precedence over the explicit arg."""
        monkeypatch.setenv(RENDERER_VAR, "stdlib")
        assert _resolve_renderer(no_input=False, renderer="rich") == "stdlib"

    def test_invalid_renderer_raises(self, monkeypatch):
        """An unknown renderer name raises InvalidConfiguration."""
        monkeypatch.delenv(RENDERER_VAR, raising=False)
        with pytest.raises(InvalidConfiguration, match="Unknown tui_forms renderer"):
            _resolve_renderer(no_input=False, renderer="not-a-renderer")

    def test_invalid_env_var_raises(self, monkeypatch):
        """An unknown renderer in the env var raises InvalidConfiguration."""
        monkeypatch.setenv(RENDERER_VAR, "bogus")
        with pytest.raises(InvalidConfiguration, match="bogus"):
            _resolve_renderer(no_input=False, renderer="rich")


class TestWizardRendererSelection:
    """Integration of _resolve_renderer with the wizard entry point."""

    def _setup_mocks(self, mock_create_form, mock_get_renderer):
        mock_form = MagicMock()
        mock_form.user_answers = {}
        mock_create_form.return_value = mock_form
        mock_renderer_instance = MagicMock()
        mock_renderer_instance.render.return_value = {"cookiecutter": {}}
        mock_get_renderer.return_value = MagicMock(return_value=mock_renderer_instance)

    def test_renderer_arg_passed_through(
        self, mock_create_form, mock_get_renderer, state, monkeypatch
    ):
        """An explicit renderer argument flows through to get_renderer."""
        monkeypatch.delenv(RENDERER_VAR, raising=False)
        self._setup_mocks(mock_create_form, mock_get_renderer)
        wizard(
            state,
            base_answers={},
            no_input=False,
            root_key="cookiecutter",
            renderer="rich",
        )
        mock_get_renderer.assert_called_once_with("rich")

    def test_env_var_overrides_renderer_arg(
        self, mock_create_form, mock_get_renderer, state, monkeypatch
    ):
        """COOKIEPLONE_RENDERER overrides the renderer argument."""
        monkeypatch.setenv(RENDERER_VAR, "stdlib")
        self._setup_mocks(mock_create_form, mock_get_renderer)
        wizard(
            state,
            base_answers={},
            no_input=False,
            root_key="cookiecutter",
            renderer="rich",
        )
        mock_get_renderer.assert_called_once_with("stdlib")

    def test_no_input_overrides_renderer_arg(
        self, mock_create_form, mock_get_renderer, state, monkeypatch
    ):
        """no_input=True forces noinput even when a renderer is provided."""
        monkeypatch.setenv(RENDERER_VAR, "rich")
        self._setup_mocks(mock_create_form, mock_get_renderer)
        wizard(
            state,
            base_answers={},
            no_input=True,
            root_key="cookiecutter",
            renderer="stdlib",
        )
        mock_get_renderer.assert_called_once_with("noinput")

    def test_invalid_renderer_raises_before_form_render(
        self, mock_create_form, mock_get_renderer, state, monkeypatch
    ):
        """An invalid renderer aborts the wizard before any rendering happens."""
        monkeypatch.delenv(RENDERER_VAR, raising=False)
        self._setup_mocks(mock_create_form, mock_get_renderer)
        with pytest.raises(InvalidConfiguration):
            wizard(
                state,
                base_answers={},
                no_input=False,
                root_key="cookiecutter",
                renderer="bogus",
            )
        mock_get_renderer.assert_not_called()
