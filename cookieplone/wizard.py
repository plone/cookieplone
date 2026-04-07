# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Implement the form wizard logic."""

import os
from typing import Any

from tui_forms import available_renderers, create_form, get_renderer

from cookieplone.config import Answers, CookieploneState
from cookieplone.exceptions import InvalidConfiguration
from cookieplone.settings import DEFAULT_EXTENSIONS, DEFAULT_RENDERER, RENDERER_VAR

NOINPUT_RENDERER = "noinput"


def _prepare_extensions(extensions: list[str]) -> list[str]:
    """Prepare the list of Jinja extensions to be used in the form wizard."""
    # Ensure that default extensions are included,
    # but allow for custom extensions as well
    all_extensions = set(DEFAULT_EXTENSIONS) | set(extensions)
    return list(all_extensions)


def _resolve_renderer(no_input: bool, renderer: str = "") -> str:
    """Resolve which tui_forms renderer to use for this run.

    Resolution order:

    1. ``no_input=True`` always forces the ``noinput`` renderer.
    2. The ``COOKIEPLONE_RENDERER`` environment variable wins over any other
       configured value, so users can override on a per-run basis.
    3. The explicit *renderer* argument (typically sourced from
       ``cookieplone-config.json``).
    4. The built-in :data:`~cookieplone.settings.DEFAULT_RENDERER`.

    :param no_input: When ``True`` the wizard is skipped; the ``noinput``
        renderer is always selected.
    :param renderer: Renderer name supplied by the caller (e.g. extracted
        from the repository-level config).  Empty string means "no preference".
    :returns: The validated renderer name.
    :raises InvalidConfiguration: If the resolved renderer name is not one
        of :func:`tui_forms.available_renderers`.
    """
    if no_input:
        return NOINPUT_RENDERER
    name = os.environ.get(RENDERER_VAR) or renderer or DEFAULT_RENDERER
    available = available_renderers()
    if name not in available:
        valid = ", ".join(sorted(available))
        raise InvalidConfiguration(
            f"Unknown tui_forms renderer {name!r}. Available renderers: {valid}."
        )
    return name


def wizard(
    state: CookieploneState,
    base_answers: dict[str, Any],
    no_input: bool = False,
    root_key: str = "",
    renderer: str = "",
) -> Answers:
    """Prompt user to enter a new config.

    :param state: The CookieploneState containing schema and other context data.
    :param base_answers: Initial answers to use as defaults.
    :param no_input: Do not prompt for user input and use only values from context.
    :param root_key: The root key for the context data.
    :param renderer: Optional ``tui_forms`` renderer name. When omitted, the
        ``COOKIEPLONE_RENDERER`` environment variable is consulted, then the
        built-in default. Ignored when ``no_input=True``.
    :raises InvalidConfiguration: If the resolved renderer name is not
        registered with ``tui_forms``.
    """
    schema = state.schema
    jinja_config: dict[str, Any] = {}
    jinja_extensions = _prepare_extensions(state.extensions)
    answers: dict[str, Any] = {}
    frm = create_form(schema, root_key=root_key)
    renderer_name = _resolve_renderer(no_input, renderer)
    renderer_klass = get_renderer(renderer_name)
    renderer_obj = renderer_klass(frm, config=jinja_config, extensions=jinja_extensions)
    answers.update(
        renderer_obj.render(initial_answers=base_answers, confirm=not no_input)
    )
    state.answers.answers = answers[root_key]
    state.answers.user_answers = frm.user_answers
    return state.answers
