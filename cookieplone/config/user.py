from cookiecutter import config
from cookieplone.exceptions import InvalidConfiguration
from cookieplone.logger import logger
from cookieplone.settings import DEFAULT_CONFIG
from cookieplone.utils.git import get_user_info
from copy import deepcopy
from pathlib import Path
from typing import Any

import os
import yaml


USER_CONFIG_ENVS = ["COOKIEPLONE_CONFIG", "COOKIECUTTER_CONFIG"]

USER_CONFIG_PATHS = [
    ".cookieplonerc",
    ".cookiecutterrc",
]


def _expand_path(path: str) -> Path:
    """Expand both environment variables and user home in the given path."""
    path = os.path.expandvars(path)
    processed = Path(path).expanduser().resolve()
    return processed


def get_config(config_path: Path) -> dict[str, Any]:
    """Retrieve the config from the specified path, returning a config dict."""

    with open(config_path, encoding="utf-8") as file_handle:
        try:
            yaml_dict = yaml.safe_load(file_handle) or {}
        except yaml.YAMLError as e:
            raise InvalidConfiguration(
                f"Unable to parse YAML file {config_path}."
            ) from e
        if not isinstance(yaml_dict, dict):
            raise InvalidConfiguration(
                f"Top-level element of YAML file {config_path} should be an object."
            )

    default_config = _get_default_config()
    config_dict = config.merge_configs(default_config, yaml_dict)

    raw_replay_dir = config_dict["replay_dir"]
    config_dict["replay_dir"] = f"{_expand_path(raw_replay_dir)}"

    raw_cookies_dir = config_dict["cookiecutters_dir"]
    config_dict["cookiecutters_dir"] = f"{_expand_path(raw_cookies_dir)}"

    return config_dict


def _get_default_config() -> dict[str, Any]:
    """Return default configuration."""
    default_config: dict[str, Any] = deepcopy(DEFAULT_CONFIG)
    for key, value in default_config.items():
        if "_dir" in key:
            default_config[key] = f"{_expand_path(value)}"
    return default_config


def _get_user_info_from_git() -> dict[str, Any]:
    """Return a partial ``default_context`` dict populated from git config.

    Reads the user's name and email from the local git configuration.  If
    the information cannot be retrieved (e.g. no git config exists, or
    gitpython raises an unexpected error), a warning is logged and an empty
    dict is returned so that callers can continue with defaults.
    """
    default_context = {}
    try:
        info = get_user_info()
    except AttributeError as e:
        logger.warning(f"Error getting git information: {e}")
    else:
        if info.email:
            default_context["email"] = info.email
        if info.name:
            default_context["fullname"] = info.name
            # Used in most templates
            default_context["author"] = info.name
    return default_context


def _get_user_config_files() -> list[Path]:
    """Return candidate user config file paths under the home directory.

    Checks each filename in :data:`USER_CONFIG_PATHS` and returns the resolved
    absolute paths. Existence is not checked here; callers are responsible for
    filtering to paths that exist.
    """
    home_path = Path.home()
    return [(home_path / filename).resolve() for filename in USER_CONFIG_PATHS]


def _get_user_config_env() -> list[Path]:
    """Return candidate config file paths from environment variables.

    Checks each variable name in :data:`USER_CONFIG_ENVS` and returns the
    paths of those that are set. Existence is not checked here; callers are
    responsible for filtering to paths that exist.
    """
    possible_locations: list[Path] = []
    for env in USER_CONFIG_ENVS:
        if env_config_file := os.environ.get(env):
            possible_locations.append(_expand_path(env_config_file))
    return possible_locations


def _get_user_config(config_file: Path | None | str) -> dict[str, Any]:
    """Load and return the user configuration dict.

    Candidate paths are evaluated in priority order — highest first:

    1. ``config_file`` (if provided)
    2. Paths from :data:`USER_CONFIG_ENVS` environment variables
    3. Well-known files under ``~`` (see :data:`USER_CONFIG_PATHS`)

    The first candidate that exists *and* contains valid YAML is used.
    Candidates with invalid YAML are skipped with a warning; if no valid
    candidate is found the default configuration is returned.
    """
    user_config = _get_default_config()
    # Priority: explicit file > env vars > well-known home-dir files
    possible_locations: list[Path] = [
        *_get_user_config_env(),
        *_get_user_config_files(),
    ]
    if config_file:
        # Explicit path wins over everything else
        config_file = f"{config_file}" if isinstance(config_file, Path) else config_file
        possible_locations.insert(0, _expand_path(config_file))

    valid_locations: list[Path] = [
        config_path for config_path in possible_locations if config_path.exists()
    ]
    for config_path in valid_locations:
        try:
            user_config = get_config(config_path)
        except InvalidConfiguration:
            logger.warning(f"Skipping invalid configuration file: {config_path}")
        else:
            logger.debug(f"Loaded configuration from {config_path}")
            break
    return user_config


def _merge_git_info(user_config: dict[str, Any]) -> None:
    """Merge information from Git config."""
    git_info = _get_user_info_from_git()
    default_context: dict[str, Any] = user_config.get("default_context", {})
    for key, value in git_info.items():
        if default_context.get(key) or not value:
            continue
        default_context[key] = value


def get_user_config(
    config_file: Path | None | str = None, default_config: dict[str, Any] | bool = False
):
    """Return the user config as a dict.

    Resolution order:

    1. If ``default_config`` is a :class:`dict`, merge it on top of the
       built-in defaults and return — no file is loaded.
    2. If ``default_config`` is ``True``, return a copy of the built-in
       defaults — no file is loaded.
    3. Otherwise load from the first valid config file found, in priority
       order:

       a. ``config_file`` (if provided)
       b. ``COOKIEPLONE_CONFIG`` environment variable
       c. ``COOKIECUTTER_CONFIG`` environment variable
       d. ``~/.cookieplonerc``
       e. ``~/.cookiecutterrc``

       If none of the above exist or contain valid YAML, the built-in
       defaults are returned.

    After the config is resolved, git user information (``fullname``,
    ``author``, and ``email``) is read from the git config and merged into
    ``default_context``.  Git values are only used as a fallback: any key
    already present in ``default_context`` (from a config file or from
    *default_config*) takes precedence and is never overwritten.
    """
    default_ = _get_default_config()
    user_config: dict[str, Any] = {}
    if default_config and isinstance(default_config, dict):
        # Do NOT load a config. Merge provided values with defaults
        # and return them instead
        user_config = dict(config.merge_configs(default_, default_config))
    elif default_config:
        # Do NOT load a config. Return defaults instead.
        logger.debug("Force ignoring user config with default_config switch.")
        user_config = default_
    else:
        user_config = _get_user_config(config_file=config_file)

    # Merge git information about the user
    _merge_git_info(user_config)
    return user_config
