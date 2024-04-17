from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional, TypeAlias

OptionalPath: TypeAlias = Optional[Path]  # noQA:UP007
OptionalListStr: TypeAlias = Optional[list[str]]  # noQA:UP007


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
