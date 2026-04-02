# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
from pathlib import Path
from typing import Any

from cookiecutter import exceptions as exc
from cookiecutter import repository as base

from cookieplone import _types as t
from cookieplone import data
from cookieplone.config import get_user_config
from cookieplone.exceptions import (
    PreFlightException,
    RepositoryException,
    RepositoryNotFound,
)

REPO_CONFIG_FILENAME = "cookieplone-config.json"

LEGACY_CONFIG_FILENAME = "cookiecutter.json"

CONFIG_FILENAMES = [
    REPO_CONFIG_FILENAME,
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
    """Resolve and return the local path of a cookieplone template repository.

    Downloads or locates the repository identified by *repository* and returns
    its resolved local :class:`~pathlib.Path`.  The user configuration (from
    *config_file* or the default config chain) supplies the abbreviation map
    and the local clone directory.

    :param repository: Repository identifier — a URL, a filesystem path, or a
        registered abbreviation (e.g. ``"gh:org/repo"``).
    :param tag: Git tag or branch to check out.  An empty string uses the
        default branch.
    :param password: Password used to decrypt a password-protected zip archive.
    :param config_file: Path to a custom cookieplone/cookiecutter config file.
        When ``None`` the default config-resolution chain is used.
    :param default_config: When ``True`` skip all config files and use
        built-in defaults.
    :returns: Resolved absolute path to the local repository directory.
    """
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
    """Open and parse the repository configuration file.

    Looks for ``cookieplone-config.json`` first.  When found, the file is
    validated against :data:`~cookieplone.config.schemas.REPOSITORY_CONFIG_SCHEMA`
    and the ``templates`` mapping is returned directly.

    Falls back to the legacy ``cookiecutter.json`` when the new format is
    not present.

    :param base_path: Root directory of the template repository.
    :returns: Parsed configuration dict containing at least a ``templates`` key.
    :raises RuntimeError: When no configuration file is found or when
        ``cookieplone-config.json`` fails validation.
    """
    repo_config_path = base_path / REPO_CONFIG_FILENAME
    if repo_config_path.exists():
        data = json.loads(repo_config_path.read_text())
        from cookieplone.config.schemas import validate_repository_config

        valid, errors = validate_repository_config(data)
        if not valid:
            msg = f"Invalid {REPO_CONFIG_FILENAME} in {base_path}:\n" + "\n".join(
                f"  - {e}" for e in errors
            )
            raise RuntimeError(msg)
        return data

    legacy_path = base_path / LEGACY_CONFIG_FILENAME
    if legacy_path.exists():
        return json.loads(legacy_path.read_text())

    raise RuntimeError(
        f"No configuration file found in {base_path}. "
        f"Expected {REPO_CONFIG_FILENAME} or {LEGACY_CONFIG_FILENAME}."
    )


def _parse_template_options(
    base_path: Path, config: dict[str, Any], all_: bool
) -> dict[str, t.CookieploneTemplate]:
    """Parse the ``"templates"`` section of a repository config and return a
    mapping of template name to :class:`~cookieplone._types.CookieploneTemplate`.

    Each entry in the ``"templates"`` dict is expected to have ``title``,
    ``description``, ``path``, and an optional ``hidden`` key.  Templates
    marked as hidden are excluded unless *all_* is ``True``.

    :param base_path: Resolved root directory of the template repository.
        Template paths are resolved relative to this directory.
    :param config: Parsed ``cookiecutter.json`` / ``cookieplone.json`` dict.
    :param all_: When ``True`` include templates that are marked as hidden.
    :returns: Ordered dict mapping each template's ``name`` to its
        :class:`~cookieplone._types.CookieploneTemplate` instance.
    """
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


def _parse_template_groups(
    base_path: Path, config: dict[str, Any], all_: bool
) -> dict[str, t.CookieploneTemplateGroup] | None:
    """Parse the ``"groups"`` section of a repository config.

    Returns an ordered dict mapping group IDs to
    :class:`~cookieplone._types.CookieploneTemplateGroup` instances, or
    ``None`` when no groups are defined in the config.

    Hidden groups (and hidden templates within visible groups) are excluded
    unless *all_* is ``True``.

    :param base_path: Resolved root directory of the template repository.
    :param config: Parsed repository config dict.
    :param all_: When ``True`` include hidden groups and templates.
    :returns: Ordered dict of groups, or ``None``.
    """
    groups_data = config.get("groups")
    if not groups_data:
        return None

    all_templates = _parse_template_options(base_path, config, all_=True)

    groups: dict[str, t.CookieploneTemplateGroup] = {}
    for group_id, group_data in groups_data.items():
        hidden = group_data.get("hidden", False)
        if hidden and not all_:
            continue
        group_templates: dict[str, t.CookieploneTemplate] = {}
        for tmpl_id in group_data.get("templates", []):
            if tmpl_id in all_templates:
                tmpl = all_templates[tmpl_id]
                if tmpl.hidden and not all_:
                    continue
                group_templates[tmpl_id] = tmpl
        if group_templates:
            groups[group_id] = t.CookieploneTemplateGroup(
                name=group_id,
                title=group_data["title"],
                description=group_data["description"],
                templates=group_templates,
                hidden=hidden,
            )
    return groups if groups else None


def get_template_groups(
    base_path: Path, all_: bool = False
) -> dict[str, t.CookieploneTemplateGroup] | None:
    """Return template groups from the repository config, or ``None``.

    :param base_path: Root directory of the template repository.
    :param all_: When ``True`` include hidden groups and templates.
    :returns: Ordered dict of groups, or ``None`` when no groups are defined.
    """
    base_path = base_path.resolve()
    config = get_repository_config(base_path)
    return _parse_template_groups(base_path, config, all_)


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
    """Resolve *template* to a local repository directory and return it.

    Expands abbreviations, then determines the source type (local path, zip
    archive, or VCS URL) and either locates or downloads the repository.  A
    sub-directory inside the repository can be targeted with *directory*.

    :param template: Repository source — a local :class:`~pathlib.Path`, a
        remote VCS URL, a zip-file URL/path, or a registered abbreviation.
    :param abbreviations: Mapping of short aliases to full repository URLs,
        as loaded from the user config.
    :param clone_to_dir: Parent directory where remote repositories are cloned
        or zip archives are unpacked.
    :param checkout: Git branch, tag, or commit to check out when cloning.
        Ignored for local paths and zip files.
    :param no_input: When ``True`` suppress interactive prompts during cloning
        or zip extraction.
    :param password: Password for decrypting a password-protected zip archive.
    :param directory: Relative sub-directory within the repository to use as
        the template root.  An empty string means the repository root.
    :returns: A ``(repo_dir, cleanup)`` tuple where *repo_dir* is the resolved
        local template directory and *cleanup* is ``True`` when the caller is
        responsible for deleting *repo_dir* after use (i.e. it was downloaded).
    :raises RepositoryNotFound: When no valid config file is found in any of
        the candidate directories.
    """
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


def _run_pre_hook(
    base_repo_dir: Path,
    repo_dir: Path,
    accept_hooks: bool,
) -> Path:
    """Run the Cookiecutter pre-prompt hook for a template repository.

    Executes the ``pre_prompt`` hook script found in ``base_repo_dir`` when
    ``accept_hooks`` is ``True``.  The hook may return a different working
    directory (for example when it sets up a sub-template), in which case the
    returned path replaces ``repo_dir``.

    If the hook exits with a non-zero status, the underlying
    ``FailedHookException`` is caught and re-raised as a
    :exc:`PreFlightException` with a human-readable message.

    :param base_repo_dir: Root directory of the checked-out template repository.
    :param repo_dir: Current working directory passed to the hook.
    :param accept_hooks: When ``False`` the hook is skipped and ``repo_dir``
        is returned unchanged.
    :returns: The (possibly updated) repository working directory.
    :raises PreFlightException: If the hook exits with a non-zero status.
    """
    from cookiecutter import hooks

    try:
        # Run pre_prompt hook
        repo_dir = Path(
            hooks.run_pre_prompt_hook(base_repo_dir) if accept_hooks else repo_dir
        )
    except exc.FailedHookException as e:
        msg = "Sanity checks failed.\nPlease review the errors above and try again."
        raise PreFlightException(msg) from e
    return repo_dir


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
    """Prepare and return a :class:`~cookieplone._types.RepositoryInfo` for a template.

    Resolves the template repository, runs the ``pre_prompt`` hook when
    requested, and collects the paths that should be removed after generation.

    :param repository: Repository source — a local path, VCS URL, zip path, or
        registered abbreviation.
    :param template_name: Logical name of the selected sub-template (used for
        replay and display purposes).
    :param template_path: Relative path inside *repository* that contains the
        sub-template's config file.  Pass an empty string to use the repository
        root.
    :param checkout: Git branch, tag, or commit to check out when cloning.
    :param no_input: When ``True`` suppress interactive prompts.
    :param accept_hooks: When ``True`` run the ``pre_prompt`` hook if one
        exists in the repository.
    :param password: Password for decrypting a password-protected zip archive.
    :param config_file: Path to a custom cookieplone/cookiecutter config file.
        When ``None`` the default config-resolution chain is used.
    :param default_config: When ``True`` skip all config files and use
        built-in defaults; when a :class:`dict` merge it on top of the defaults.
    :returns: A fully populated :class:`~cookieplone._types.RepositoryInfo`
        instance ready for use by the generator.
    :raises PreFlightException: If the ``pre_prompt`` hook exits with a
        non-zero status.
    :raises RepositoryNotFound: If the template source cannot be resolved to a
        valid local directory.
    """
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
    cleanup_base_repo_dir = bool(cleanup_base_repo_dir)
    repo_dir, cleanup_repo = base_repo_dir, cleanup_base_repo_dir

    # Root of the local repository
    root_repo_dir = Path(
        str(base_repo_dir).replace(str(template_path), "")
        if template_path
        else base_repo_dir
    ).resolve()

    base_repo_dir = Path(base_repo_dir)

    # Extract global versions from the repository-level config (if present).
    global_versions: dict[str, str] = {}
    if _repository_has_config(root_repo_dir):
        try:
            repo_config = get_repository_config(root_repo_dir)
            global_versions = repo_config.get("config", {}).get("versions", {})
        except RuntimeError:
            pass

    repo_dir = _run_pre_hook(base_repo_dir, repo_dir, accept_hooks)

    # Prepare cleanup_paths
    cleanup_paths = []
    if cleanup_base_repo_dir:
        cleanup_paths.append(base_repo_dir)
    if cleanup_repo or (repo_dir != base_repo_dir):
        cleanup_paths.append(repo_dir)
    return t.RepositoryInfo(
        repository=str(repository),
        base_repo_dir=base_repo_dir,
        repo_dir=repo_dir,
        root_repo_dir=root_repo_dir,
        replay_dir=replay_dir,
        checkout=checkout,
        template_name=template_name,
        accept_hooks=accept_hooks,
        config_dict=config_dict,
        global_versions=global_versions,
        cleanup_paths=cleanup_paths,
    )
