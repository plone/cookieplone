# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Implement the form wizard logic."""

from typing import Any

from tui_forms import create_form, get_renderer

from cookieplone.config import Answers, CookieploneState
from cookieplone.settings import DEFAULT_EXTENSIONS


def _prepare_extensions(extensions: list[str]) -> list[str]:
    """Prepare the list of Jinja extensions to be used in the form wizard."""
    # Ensure that default extensions are included,
    # but allow for custom extensions as well
    all_extensions = set(DEFAULT_EXTENSIONS) | set(extensions)
    return list(all_extensions)


def wizard(
    state: CookieploneState,
    base_answers: dict[str, Any],
    no_input: bool = False,
    root_key: str = "",
) -> Answers:
    """Prompt user to enter a new config.

    :param state: The CookieploneState containing schema and other context data.
    :param base_answers: Initial answers to use as defaults.
    :param no_input: Do not prompt for user input and use only values from context.
    :param root_key: The root key for the context data.
    """
    schema = state.schema
    jinja_config: dict[str, Any] = {}
    jinja_extensions = _prepare_extensions(state.extensions)
    answers: dict[str, Any] = {}
    frm = create_form(schema, root_key=root_key)
    renderer_name = "noinput" if no_input else "cookiecutter"
    renderer_klass = get_renderer(renderer_name)
    renderer = renderer_klass(frm, config=jinja_config, extensions=jinja_extensions)
    answers.update(renderer.render(initial_answers=base_answers, confirm=not no_input))
    state.answers.answers = answers[root_key]
    state.answers.user_answers = frm.user_answers
    return state.answers
