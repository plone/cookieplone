# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
from pathlib import Path

from cookiecutter.config import get_user_config
from cookiecutter.repository import determine_repo_dir

from cookieplone import data


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


def get_template_options(base_path: Path) -> list[list[str]]:
    """Parse cookiecutter.json and return a list of template options."""
    config = json.loads((base_path / "cookiecutter.json").read_text())
    available_templates = config.get("templates", {})
    templates = []
    for idx, name in enumerate(available_templates, start=1):
        idx = str(idx)
        value = available_templates[name]
        title = value["title"]
        description = value["description"]
        templates.append((idx, name, title, description))
    return templates
