# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
from pathlib import Path
from typing import Any

from cookiecutter import exceptions as exc
from cookiecutter import repository as base
from cookiecutter.config import get_user_config
from cookiecutter.hooks import run_pre_prompt_hook

from cookieplone import _types as t
from cookieplone import data
from cookieplone.exceptions import RepositoryException, RepositoryNotFound

CONFIG_FILENAME = "cookiecutter.json"

CONFIG_FILENAMES = [
    "cookiecutter.json",
    "cookieplone.json",
]


def get_base_repository(
    repository: str,
    tag: str = "",
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
        clone_to_dir=Path(config_dict["cookiecutters_dir"]),
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


def _repository_has_config(repo_directory: Path):
    """Determine if `repo_directory` contains a `cookiecutter.json` file.

    :param repo_directory: The candidate repository directory.
    :return: True if the `repo_directory` is valid, else False.
    """
    status = False
    if repo_directory and repo_directory.is_dir() and repo_directory.exists():
        for filename in CONFIG_FILENAMES:
            if (repo_directory / filename).exists():
                return True
    return status


def _repository_from_zip(
    template: str, clone_to_dir, no_input, password
) -> tuple[list[Path], bool]:
    """Prepare a repository from a zip file."""
    try:
        unzipped_dir = base.unzip(
            zip_uri=template,
            is_url=base.is_repo_url(template),
            clone_to_dir=clone_to_dir,
            no_input=no_input,
            password=password,
        )
    except exc.InvalidZipRepository as e:
        raise RepositoryException("Invalid Zip repository") from e
    return [Path(unzipped_dir)], True


def _repository_from_vcs(
    template: str, clone_to_dir, no_input, checkout
) -> tuple[list[Path], bool]:
    """Prepare a repository from a vcs url."""
    try:
        cloned_repo = base.clone(
            repo_url=template,
            checkout=checkout,
            clone_to_dir=clone_to_dir,
            no_input=no_input,
        )
    except exc.RepositoryCloneFailed as e:
        raise RepositoryException(f"Invalid vcs repository {template}") from e
    return [Path(cloned_repo)], True


def determine_repo_dir(
    template: str | Path,
    abbreviations: dict[str, str],
    clone_to_dir: Path,
    checkout: str = "",
    no_input: bool = False,
    password: str = "",
    directory: str = "",
) -> tuple[Path, bool]:
    if isinstance(template, str):
        template = str(base.expand_abbreviations(template, abbreviations))

    if isinstance(template, Path):
        repository_candidates = [Path(template), clone_to_dir / template]
        cleanup = False
    elif base.is_zip_file(template):
        repository_candidates, cleanup = _repository_from_zip(
            template, clone_to_dir, no_input, password
        )
    elif base.is_repo_url(template):
        repository_candidates, cleanup = _repository_from_vcs(
            template, clone_to_dir, no_input, checkout
        )
    else:
        repository_candidates = [Path(template), clone_to_dir / template]
        cleanup = False

    if directory:
        repository_candidates = [s / directory for s in repository_candidates]

    for repo_candidate in repository_candidates:
        if _repository_has_config(repo_candidate):
            return repo_candidate, cleanup

    locations = "\n".join([f"{path}" for path in repository_candidates])
    raise RepositoryNotFound(
        f'A valid repository for "{template}" could not be found in the following '
        f"locations:\n{locations}"
    )


def get_repository(
    repository: str | Path,
    template_name: str,
    template_path: str,
    checkout: str = "",
    no_input: bool = False,
    accept_hooks: bool = True,
    password: str = "",
    config_file: Path | str | None = None,
    default_config: dict[str, Any] | bool = False,
) -> t.RepositoryInfo:
    """Repository."""
    config_dict = get_user_config(
        config_file=config_file,
        default_config=default_config,
    )
    replay_dir = Path(config_dict["replay_dir"])
    base_repo_dir, cleanup_base_repo_dir = determine_repo_dir(
        template=repository,
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=Path(config_dict["cookiecutters_dir"]),
        checkout=checkout,
        no_input=no_input,
        password=password,
        directory=template_path,
    )
    base_repo_dir = str(base_repo_dir)
    cleanup_base_repo_dir = bool(cleanup_base_repo_dir)
    repo_dir, cleanup_repo = base_repo_dir, cleanup_base_repo_dir

    # Root of the local repository
    root_repo_dir = Path(
        str(base_repo_dir).replace(str(template_path), "")
        if template_path
        else base_repo_dir
    ).resolve()

    base_repo_dir = Path(base_repo_dir)

    try:
        # Run pre_prompt hook
        repo_dir = Path(
            run_pre_prompt_hook(base_repo_dir) if accept_hooks else repo_dir
        )
    except exc.FailedHookException as e:
        raise e

    # Always remove temporary dir if it was created
    cleanup_repo = cleanup_repo or (repo_dir != base_repo_dir)
    return t.RepositoryInfo(
        repository=str(repository),
        base_repo_dir=base_repo_dir,
        cleanup_base=cleanup_base_repo_dir,
        repo_dir=repo_dir,
        root_repo_dir=root_repo_dir,
        replay_dir=replay_dir,
        checkout=checkout,
        template_name=template_name,
        cleanup_repo=cleanup_repo,
        accept_hooks=accept_hooks,
        config_dict=config_dict,
    )
