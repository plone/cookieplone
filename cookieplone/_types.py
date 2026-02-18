from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class CookieploneTemplate:
    path: Path
    name: str
    title: str
    description: str
    hidden: bool = False


class AnswerValidator(Protocol):
    def __name__(self) -> str: ...
    def __call__(self, value: str) -> bool: ...
