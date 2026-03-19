# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING

from cookiecutter import exceptions as exc

if TYPE_CHECKING:
    from cookieplone.config.state import CookieploneState


class CookieploneException(Exception):
    """Cookieplone base exception."""

    message: str

    def __init__(self, message: str):
        self.message = message


class PreFlightException(CookieploneException):
    """Exception raised when a pre-prompt-hook fails."""

    message: str

    def __init__(self, message: str):
        self.message = message


class GeneratorException(CookieploneException):
    """Cookieplone generator exception."""

    message: str
    original: Exception | None = None

    def __init__(
        self, message: str, state: CookieploneState, original: Exception | None = None
    ):
        """Initialise with a human-readable message, the current run state, and
        the original exception.

        :param message: Description of the failure.
        :param state: The ``CookieploneState`` at the time of failure,
            preserved so it can be persisted for replay.
        :param original: The underlying exception that triggered this one, if any.
        """
        self.message = message
        self.original = original
        self.state = state


class RepositoryException(exc.CookiecutterException):
    """Repository-related exception.

    Raised when there is an issue obtaining a repository.
    """


class RepositoryNotFound(RepositoryException):
    """Exception for missing repo.

    Raised when the specified cookieplone repository doesn't exist.
    """


class FailedHookException(exc.FailedHookException):
    """Raised when a cookiecutter hook script exits with a non-zero status."""


class InvalidConfiguration(exc.InvalidConfiguration):
    """Raised when a configuration is invalid."""
