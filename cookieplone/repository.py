# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
from pathlib import Path
from typing import Any

from cookiecutter.config import get_user_config
from cookiecutter.repository import determine_repo_dir

from cookieplone import _types as t
from cookieplone import data

CONFIG_FILENAME = "cookiecutter.json"


def get_base_repository(
    repository: str,
    tag: str | None = None,
    password: str = "",
    config_file: data.OptionalPath = None,
    default_config: bool = False,
) -> Path:
    config_dict = get_user_config(
        config_file=config_file,
        default_config=default_config,
    )
    base_repo_dir, _ = determine_repo_dir(
        template=repository,
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=config_dict["cookiecutters_dir"],
        checkout=tag,
        no_input=True,  # Force download
        password=password,
        directory="",
    )
    base_repo_dir = Path(base_repo_dir).resolve()
    return base_repo_dir


def get_repository_config(base_path: Path) -> dict[str, Any]:
    """Open and parse the repository configuration file."""
    path = base_path / CONFIG_FILENAME
    if not path.exists():
        raise RuntimeError(f"{CONFIG_FILENAME} not found in {base_path}")
    return json.loads(path.read_text())


def _parse_template_options(
    base_path: Path, config: dict[str, Any], all_: bool
) -> dict[str, t.CookieploneTemplate]:
    available_templates = config.get("templates", {})
    templates = {}
    for name in available_templates:
        value = available_templates[name]
        hidden = value.get("hidden", False)
        if hidden and not all_:
            # Do not list a hidden template
            continue
        title = value["title"]
        description = value["description"]
        path: Path = (base_path / value["path"]).resolve()
        template = t.CookieploneTemplate(
            path.relative_to(base_path), name, title, description, hidden
        )
        templates[template.name] = template
    return templates


def get_template_options(
    base_path: Path, all_: bool = False
) -> dict[str, t.CookieploneTemplate]:
    """Parse cookiecutter.json and return a dict of template options."""
    base_path = base_path.resolve()
    config = get_repository_config(base_path)
    return _parse_template_options(base_path, config, all_)
