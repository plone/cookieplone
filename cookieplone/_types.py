from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CookieploneTemplate:
    """A template available in a cookieplone repository."""

    path: Path
    name: str
    title: str
    description: str
    hidden: bool = False


@dataclass
class RepositoryInfo:
    """Resolved repository state for a cookieplone run.

    Groups all repository-related paths and configuration that are
    determined once during repository setup and then passed through
    the generation pipeline.
    """

    repository: str
    base_repo_dir: Path
    repo_dir: Path
    root_repo_dir: Path
    replay_dir: Path
    template_name: str
    checkout: str
    accept_hooks: bool
    config_dict: dict[str, Any]
    cleanup_paths: list[Path] = field(default_factory=list)


@dataclass
class RunConfig:
    """Runtime options controlling how template generation is executed.

    Groups the flags and paths that govern file generation behaviour,
    hook execution, and conflict handling.
    """

    output_dir: Path
    no_input: bool
    accept_hooks: bool
    overwrite_if_exists: bool
    skip_if_file_exists: bool
    keep_project_on_failure: bool
