# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
import shutil
from pathlib import Path

from cookiecutter.utils import force_delete


def rmtree(path: Path | str):
    """Remove a directory and all its contents. Like rm -rf on Unix.

    :param path: A directory path.
    """
    shutil.rmtree(path, onexc=force_delete)


def resolve_path(path: Path | str) -> Path:
    """Resolve a path, including home user expansion."""
    path = Path(path)
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


def load_json(path: Path) -> dict:
    """Load a JSON file and return its contents as a dictionary."""
    with path.open() as f:
        return json.load(f)


def load_config_file(path: Path | str) -> dict:
    """Load a config file and return its contents as a dictionary."""
    path = resolve_path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} does not exist.")
    return load_json(path)
