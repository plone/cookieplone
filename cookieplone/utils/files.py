# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

from cookiecutter.utils import rmtree


def resolve_path(path: Path | str) -> Path:
    """Resolve a path, including home user expansion."""
    if f"{path}".startswith("~"):
        path = path.expanduser()
    return path.resolve()


def remove_files(base_path: Path, paths: list[str]):
    """Remove files."""
    for filepath in paths:
        path = base_path / filepath
        exists = path.exists()
        if exists and path.is_dir():
            rmtree(path)
        elif exists and path.is_file():
            path.unlink()


def remove_gha(base_path: Path):
    """Remove GHA folder."""
    remove_files(base_path=base_path, paths=[".github"])
