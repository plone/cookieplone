# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT


def parse_boolean(value: str) -> bool:
    """Parse a string value into a boolean.

    Recognises ``"1"``, ``"yes"`` and ``"y"`` (case-insensitive) as truthy.
    All other values are considered falsy.

    :param value: The string to parse.
    :returns: ``True`` if the value is truthy, ``False`` otherwise.
    """
    return value.lower() in ("1", "yes", "y")
