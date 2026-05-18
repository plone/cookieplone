# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from cookiecutter import exceptions as exc
from cookiecutter import repository as base
from cookieplone import _types as t
from cookieplone import data
from cookieplone.config import get_user_config
from cookieplone.config.merge import ORIGINS_KEY
from cookieplone.config.merge import merge_repo_configs
from cookieplone.config.merge import normalize_extends
from cookieplone.exceptions import InvalidConfiguration
from cookieplone.exceptions import PreFlightException
from cookieplone.exceptions import RepositoryException
from cookieplone.exceptions import RepositoryNotFound
from cookieplone.exceptions import VersionTooOldException
from packaging.version import Version
from pathlib import Path
from typing import Any

import json


REPO_CONFIG_FILENAME = "cookieplone-config.json"

LEGACY_CONFIG_FILENAME = "cookiecutter.json"

CONFIG_FILENAMES = [
    REPO_CONFIG_FILENAME,
    "cookiecutter.json",
    "cookieplone.json",
]

MAX_EXTENDS_DEPTH = 5

# Cache keyed by the resolved string form of a repository's base path.
# Each entry holds ``(merged_config, cleanup_paths, upstream_repos)`` —
# populated by ``get_repository_config`` the first time it resolves a config
# with an ``extends`` field, then returned verbatim on subsequent calls so
# the upstream is not re-cloned per lookup.
_RESOLUTION_CACHE: dict[str, tuple[dict[str, Any], list[Path], list[Path]]] = {}


def _clear_resolution_cache() -> None:
    """Reset the in-process extends resolution cache.

    Intended for test setup/teardown.  Does not delete any filesystem state;
    cleanup of cloned upstream directories is the responsibility of the
    :class:`~cookieplone._types.RepositoryInfo` that captured them.
    """
    _RESOLUTION_CACHE.clear()


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
    if _repository_has_config(base_repo_dir):
        repo_config = get_repository_config(base_repo_dir)
        _check_min_version(repo_config.get("config", {}))
    return base_repo_dir


def _load_raw_repository_config(base_path: Path) -> dict[str, Any]:
    """Load and validate the repo config file at *base_path* without resolving
    ``extends``.

    Used by :func:`_resolve_extends` so the recursive resolver retains full
    control of cycle and depth tracking; the public
    :func:`get_repository_config` wraps this with caching and extends merging.

    :param base_path: Root directory of the template repository.
    :returns: Raw parsed configuration dict.
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


def get_repository_config(base_path: Path) -> dict[str, Any]:
    """Load the repository config file and resolve any ``extends`` chain.

    The configuration is loaded via :func:`_load_raw_repository_config` and,
    when the config declares an ``extends`` field, the upstream repository
    (and any transitive ones) is resolved and merged on top.  The returned
    dict is the merged result and carries a top-level ``_template_origins``
    mapping used by :func:`_parse_template_options` to resolve each template's
    path against its origin repository.

    Resolution results are cached in :data:`_RESOLUTION_CACHE` keyed by the
    resolved *base_path* so subsequent lookups during the same run do not
    re-clone the upstream.  Cleanup paths and ``upstream_repos`` recorded at
    resolution time are picked up by :func:`get_repository` and propagated to
    the resulting :class:`~cookieplone._types.RepositoryInfo`.

    :param base_path: Root directory of the template repository.
    :returns: Parsed configuration dict, possibly merged with one or more
        upstream configs.
    :raises RuntimeError: When no configuration file is found or when the
        loaded or merged ``cookieplone-config.json`` fails validation.
    :raises InvalidConfiguration: On cycle or depth-limit violations during
        ``extends`` resolution.
    :raises RepositoryException: When an upstream cannot be resolved.
    """
    cache_key = str(Path(base_path).resolve())
    if cache_key in _RESOLUTION_CACHE:
        return _RESOLUTION_CACHE[cache_key][0]

    data = _load_raw_repository_config(base_path)
    extends = data.get("extends") if isinstance(data, dict) else None
    if extends:
        merged, cleanup_paths, upstream_repos = _resolve_and_merge_extends(
            downstream_config=data,
            downstream_repo_dir=Path(base_path).resolve(),
            extends=extends,
        )
        _RESOLUTION_CACHE[cache_key] = (merged, cleanup_paths, upstream_repos)
        return merged

    _RESOLUTION_CACHE[cache_key] = (data, [], [])
    return data


def _resolve_and_merge_extends(
    downstream_config: dict[str, Any],
    downstream_repo_dir: Path,
    extends: Any,
) -> tuple[dict[str, Any], list[Path], list[Path]]:
    """Resolve a downstream's ``extends`` and merge it on top.

    Loads the current user config (for abbreviations and clone directory),
    delegates resolution and recursion to :func:`_resolve_extends`, then
    folds the resolved upstream stack underneath *downstream_config* via
    :func:`merge_repo_configs`.  Cross-referential checks on the merged
    result are re-run because the merged dict no longer carries ``extends``.

    :param downstream_config: Raw downstream config (already structurally
        validated).
    :param downstream_repo_dir: Resolved local path of the downstream repo.
    :param extends: The downstream's ``extends`` value (string or object).
    :returns: ``(merged_config, cleanup_paths, upstream_repos)`` — the merged
        dict (with ``_template_origins``), the list of clone directories the
        caller must delete after the run, and the list of upstream repo
        directories (closest-to-downstream first) for
        :attr:`~cookieplone._types.RepositoryInfo.upstream_repos`.
    :raises RuntimeError: When the merged config fails cross-referential
        validation.
    """
    user_config = get_user_config()
    upstream_config, upstream_repo_dir, cleanup_paths = _resolve_extends(
        extends,
        abbreviations=user_config["abbreviations"],
        clone_to_dir=Path(user_config["cookiecutters_dir"]),
    )
    merged = merge_repo_configs(
        upstream_config,
        downstream_config,
        upstream_repo_dir=upstream_repo_dir,
        downstream_repo_dir=downstream_repo_dir,
    )
    merged.pop("extends", None)

    from cookieplone.config.schemas import validate_repository_config

    # Strip the internal sidecar before structural revalidation.
    sidecar = merged.pop(ORIGINS_KEY, None)
    valid, errors = validate_repository_config(merged)
    if sidecar is not None:
        merged[ORIGINS_KEY] = sidecar
    if not valid:
        joined = "\n".join(f"  - {e}" for e in errors)
        raise RuntimeError(
            f"Invalid merged {REPO_CONFIG_FILENAME} after resolving 'extends':\n"
            f"{joined}"
        )

    # Derive the list of distinct upstream repo dirs from the merged origins
    # so transitively-inherited templates contribute their origins too.
    seen: set[Path] = set()
    upstream_repos: list[Path] = []
    for origin_str in merged.get(ORIGINS_KEY, {}).values():
        origin = Path(origin_str)
        if origin == downstream_repo_dir or origin in seen:
            continue
        seen.add(origin)
        upstream_repos.append(origin)
    return merged, cleanup_paths, upstream_repos


def _parse_template_options(
    base_path: Path, config: dict[str, Any], all_: bool
) -> dict[str, t.CookieploneTemplate]:
    """Parse the ``"templates"`` section of a repository config and return a
    mapping of template name to :class:`~cookieplone._types.CookieploneTemplate`.

    Each entry in the ``"templates"`` dict is expected to have ``title``,
    ``description``, ``path``, and an optional ``hidden`` key.  Templates
    marked as hidden are excluded unless *all_* is ``True``.

    When the config carries a top-level ``_template_origins`` mapping
    (produced by :func:`cookieplone.config.merge.merge_repo_configs`), each
    template's ``path`` is resolved against its recorded origin repository
    and the resulting :class:`~cookieplone._types.CookieploneTemplate`
    carries the origin so callers can target the correct repo at generation
    time.  Templates without an entry in the sidecar fall back to
    *base_path*.

    :param base_path: Resolved root directory of the template repository.
        Used as the default origin when no ``_template_origins`` entry exists.
    :param config: Parsed ``cookiecutter.json`` / ``cookieplone.json`` dict.
    :param all_: When ``True`` include templates that are marked as hidden.
    :returns: Ordered dict mapping each template's ``name`` to its
        :class:`~cookieplone._types.CookieploneTemplate` instance.
    """
    available_templates = config.get("templates", {})
    origins = config.get(ORIGINS_KEY, {})
    templates: dict[str, t.CookieploneTemplate] = {}
    for name in available_templates:
        value = available_templates[name]
        hidden = value.get("hidden", False)
        if hidden and not all_:
            continue
        title = value["title"]
        description = value["description"]
        origin = Path(origins[name]).resolve() if name in origins else base_path
        absolute_path = (origin / value["path"]).resolve()
        try:
            relative_path = absolute_path.relative_to(origin)
        except ValueError:
            relative_path = absolute_path
        template = t.CookieploneTemplate(
            relative_path, name, title, description, hidden, origin=origin
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


def _resolve_extends(
    extends: Any,
    abbreviations: dict[str, str],
    clone_to_dir: Path,
    no_input: bool = False,
    password: str = "",
    parent_chain: list[str] | None = None,
    depth: int = 0,
) -> tuple[dict[str, Any], Path, list[Path]]:
    """Resolve a repository's ``extends`` reference recursively.

    Clones (or locates) the upstream repository, loads and validates its
    ``cookieplone-config.json``, and — if the upstream itself declares an
    ``extends`` — recurses into that, merging each layer with downstream-wins
    semantics via :func:`cookieplone.config.merge.merge_repo_configs`.

    Cycles are detected through ``parent_chain`` (the list of normalised URLs
    visited along the current resolution path).  The recursion is also bounded
    by :data:`MAX_EXTENDS_DEPTH` to prevent runaway chains.

    :param extends: Raw ``extends`` value as parsed from the downstream config —
        either a string (URL) or an object with ``url`` and optional ``tag``.
        Empty/``None`` is a usage error; this helper should only be called when
        ``extends`` is actually set.
    :param abbreviations: User-config abbreviation map for short URLs.
    :param clone_to_dir: Parent directory where upstream clones are placed.
    :param no_input: When ``True`` suppress interactive prompts during cloning.
    :param password: Password for password-protected zip archives.
    :param parent_chain: Internal — list of normalised URLs already on the
        current resolution path.  Used for cycle detection.
    :param depth: Internal — recursion depth, for the depth-limit check.
    :returns: A ``(config, repo_dir, cleanup_paths)`` tuple where *config* is
        the fully resolved (and recursively merged) upstream configuration with
        ``_template_origins`` stamped, *repo_dir* is the directory of the
        first-level upstream clone (for the caller's subsequent merge step),
        and *cleanup_paths* lists every directory created during resolution
        that the caller must delete after the run.
    :raises InvalidConfiguration: When a cycle is detected, when the depth
        limit is exceeded, or when ``extends`` is malformed.
    :raises RepositoryException: When the upstream repository cannot be
        resolved (unreachable URL, invalid zip, missing config, etc.).
    """
    parent_chain = list(parent_chain or [])
    normalized = normalize_extends(extends)
    if normalized is None:
        raise InvalidConfiguration(
            "_resolve_extends called with an empty 'extends' value."
        )
    url = normalized["url"]
    tag = normalized["tag"] or ""

    if url in parent_chain:
        cycle = " -> ".join([*parent_chain, url])
        raise InvalidConfiguration(f"Circular 'extends' detected: {cycle}")
    if depth >= MAX_EXTENDS_DEPTH:
        chain = " -> ".join([*parent_chain, url])
        raise InvalidConfiguration(
            f"'extends' depth limit ({MAX_EXTENDS_DEPTH}) exceeded: {chain}"
        )

    try:
        repo_dir, cleanup = determine_repo_dir(
            template=url,
            abbreviations=abbreviations,
            clone_to_dir=clone_to_dir,
            checkout=tag,
            no_input=no_input,
            password=password,
            directory="",
        )
    except (RepositoryException, RepositoryNotFound) as e:
        raise RepositoryException(
            f"Could not resolve 'extends' upstream {url!r}: {e}"
        ) from e

    repo_dir = Path(repo_dir).resolve()
    cleanup_paths: list[Path] = [repo_dir] if cleanup else []

    config = _load_raw_repository_config(repo_dir)

    further = config.get("extends")
    if further:
        nested_config, nested_repo_dir, nested_cleanup = _resolve_extends(
            further,
            abbreviations=abbreviations,
            clone_to_dir=clone_to_dir,
            no_input=no_input,
            password=password,
            parent_chain=[*parent_chain, url],
            depth=depth + 1,
        )
        config = merge_repo_configs(
            nested_config,
            config,
            upstream_repo_dir=nested_repo_dir,
            downstream_repo_dir=repo_dir,
        )
        cleanup_paths.extend(nested_cleanup)

    return config, repo_dir, cleanup_paths


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


def _check_min_version(config_section: dict[str, Any]) -> None:
    """Raise if the installed cookieplone is older than ``config.min_version``.

    :param config_section: The ``config`` dict from ``cookieplone-config.json``.
    :raises VersionTooOldException: When the installed version is too old.
    """
    min_version_str = config_section.get("min_version", "")
    if not min_version_str:
        return
    from cookieplone import __version__

    installed = Version(__version__)
    required = Version(min_version_str)
    if installed < required:
        msg = (
            f"This repository requires cookieplone >= {required}, "
            f"but you have {installed} installed.\n"
            f"Please upgrade:  uvx --no-cache cookieplone@{required}"
        )
        raise VersionTooOldException(msg)


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

    # Extract global versions and renderer preference from the
    # repository-level config (if present).  When the config declares
    # ``extends`` this also resolves upstreams; the resolution cache
    # entry exposes the cleanup paths and upstream repos for inclusion
    # on the returned RepositoryInfo.
    global_versions: dict[str, str] = {}
    renderer: str = ""
    extends_cleanup: list[Path] = []
    upstream_repos: list[Path] = []
    if _repository_has_config(root_repo_dir):
        try:
            repo_config = get_repository_config(root_repo_dir)
            repo_config_section = repo_config.get("config", {})
            global_versions = repo_config_section.get("versions", {})
            renderer = repo_config_section.get("renderer", "")
            _check_min_version(repo_config_section)
            cache_entry = _RESOLUTION_CACHE.get(str(root_repo_dir.resolve()))
            if cache_entry is not None:
                _, extends_cleanup, upstream_repos = cache_entry
        except RuntimeError:
            pass

    repo_dir = _run_pre_hook(base_repo_dir, repo_dir, accept_hooks)

    # Prepare cleanup_paths
    cleanup_paths = []
    if cleanup_base_repo_dir:
        cleanup_paths.append(base_repo_dir)
    if cleanup_repo or (repo_dir != base_repo_dir):
        cleanup_paths.append(repo_dir)
    cleanup_paths.extend(extends_cleanup)
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
        renderer=renderer,
        cleanup_paths=cleanup_paths,
        upstream_repos=upstream_repos,
    )
