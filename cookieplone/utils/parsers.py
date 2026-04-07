# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT


def parse_boolean(value: str | bool | int) -> bool:
    """Parse a value into a boolean.

    For strings, recognises ``"1"``, ``"yes"`` and ``"y"`` (case-insensitive)
    as truthy; all other strings are falsy. Booleans and integers are returned
    using their natural Python truthiness, so the helper can be safely called
    from filter chains that may receive either a v1 string default or a v2
    schema boolean.

    :param value: The value to parse.
    :returns: ``True`` if the value is truthy, ``False`` otherwise.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return value.lower() in ("1", "yes", "y")
