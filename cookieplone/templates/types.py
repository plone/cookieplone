from pathlib import Path
from typing import Protocol

StrPath = str | Path
DataStructure = dict | list


class VariableFinder(Protocol):
    def __call__(self, data: str) -> set: ...


class VariableValidator(Protocol):
    def __call__(self, key: str, ignore: list[str] | None) -> bool: ...
