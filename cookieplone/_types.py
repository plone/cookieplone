from dataclasses import dataclass
from pathlib import Path


@dataclass
class CookieploneTemplate:
    path: Path
    name: str
    title: str
    description: str
    hidden: bool = False
