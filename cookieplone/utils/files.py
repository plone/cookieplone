# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
from collections import OrderedDict
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


def load_json(
    path: Path, as_ordered: bool = False, encoding: str = "utf-8"
) -> dict | OrderedDict:
    """Load a JSON file and return its contents as a dictionary."""
    with path.open(encoding=encoding) as f:
        factory = OrderedDict if as_ordered else dict
        return json.load(f, object_hook=factory)


def load_config_file(path: Path | str, as_ordered: bool = False) -> dict:
    """Load a config file and return its contents as a dictionary."""
    path = resolve_path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} does not exist.")
    return load_json(path, as_ordered)


def save_json(path: Path, data: dict, encoding: str = "utf-8") -> dict | OrderedDict:
    """Save a dictionary as a JSON file."""
    with path.open("w", encoding=encoding) as f:
        json.dump(data, f, indent=4)
    return data
