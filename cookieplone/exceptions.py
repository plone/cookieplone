# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
class CookieploneException(Exception):
    """Cookieplone base exception."""

    message: str

    def __init__(self, message: str):
        self.message = message


class GeneratorException(CookieploneException):
    """Cookieplone generator exception."""

    message: str
    original: Exception | None = None

    def __init__(self, message: str, original: Exception | None = None):
        self.message = message
        self.original = original
