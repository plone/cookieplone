# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Literal
from typing import TypeAlias


OptionalPath: TypeAlias = Path | None
OptionalListStr: TypeAlias = list[str] | None


@dataclass
class SanityCheck:
    """Definition of a sanity check."""

    name: str
    func: Callable
    args: list[Any]
    level: Literal["info", "warning", "error"]


@dataclass
class SanityCheckResult:
    """Result of a sanity check."""

    name: str
    status: bool
    message: str = ""


@dataclass
class SanityCheckResults:
    """Results of all sanity checks."""

    status: bool
    checks: list[SanityCheckResult]
    message: str = ""


@dataclass
class ItemValidator:
    """Validate an answer provided by the user."""

    key: str
    func: Callable
    level: Literal["info", "warning", "error"] = "error"


@dataclass
class ItemValidatorResult:
    """Result of an item validation."""

    key: str
    status: bool
    message: str = ""


@dataclass
class ContextValidatorResult:
    """Results of all validations checks."""

    status: bool
    validations: list[ItemValidatorResult]
    message: str = ""
