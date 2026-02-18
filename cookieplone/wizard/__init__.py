# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Implement the form wizard logic."""

from collections import OrderedDict
from typing import Any

from cookieplone.wizard import parser


def wizard(context: dict[str, Any], no_input: bool = False) -> OrderedDict[str, Any]:
    """Prompt user to enter a new config.

    :param dict context: Source for field names and sample values.
    :param no_input: Do not prompt for user input and use only values from context.
    """
    form_wizard = parser.parse_config_v1(context, no_input=no_input)
    answers = form_wizard.run()
    return answers
