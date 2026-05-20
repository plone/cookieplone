from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any


@dataclass
class CookieploneTemplate:
    """A template available in a cookieplone repository.

    :param path: Template path relative to ``origin``.
    :param name: Logical template identifier.
    :param title: Display title.
    :param description: Display description.
    :param hidden: Whether the template is hidden from the default menu.
    :param origin: Local path to the repository the template lives in.
        For inherited templates this points at an upstream clone; for
        local templates it is the downstream repository root.  Defaults
        to ``None`` for backwards compatibility with code that constructs
        :class:`CookieploneTemplate` without an explicit origin.
    :param underlay: For templates redeclared on top of an upstream version,
        the list of prior layers as ``(origin_repo_dir, relative_path)``
        pairs in upstream-first order.  Empty for templates without an
        underlying upstream version.  Used by the generator to overlay the
        downstream template directory on top of upstream files so a
        downstream can override individual files (e.g. ``README.md``)
        without copying the whole upstream tree.
    """

    path: Path
    name: str
    title: str
    description: str
    hidden: bool = False
    origin: Path | None = None
    underlay: list[tuple[Path, str]] = field(default_factory=list)


@dataclass
class CookieploneTemplateGroup:
    """A named group of related templates in a cookieplone repository."""

    name: str
    title: str
    description: str
    templates: dict[str, "CookieploneTemplate"]
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
    global_versions: dict[str, str] = field(default_factory=dict)
    renderer: str = ""
    cleanup_paths: list[Path] = field(default_factory=list)
    upstream_repos: list[Path] = field(default_factory=list)


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


@dataclass
class GenerateConfig:
    """Complete configuration for a single :func:`generate` invocation.

    Consolidates all parameters previously passed as positional arguments
    into a structured object with proper type annotations and sensible
    defaults.
    """

    repository: str | Path
    template_name: str
    output_dir: Path
    tag: str = ""
    no_input: bool = False
    extra_context: dict[str, Any] | None = None
    replay: Path | bool = False
    overwrite_if_exists: bool = False
    config_file: Path | None = None
    default_config: dict[str, Any] | bool = False
    passwd: str | None = None
    template_path: str | None = None
    skip_if_file_exists: bool = False
    keep_project_on_failure: bool = False
    dump_answers: bool = True
    global_versions: dict[str, str] | None = None
    template_underlay: list[tuple[Path, str]] | None = None
    upstream_repos: list[Path] | None = None

    def to_run_config(self) -> RunConfig:
        """Build a :class:`RunConfig` from this generation configuration."""
        return RunConfig(
            output_dir=self.output_dir,
            no_input=self.no_input,
            accept_hooks=True,
            overwrite_if_exists=self.overwrite_if_exists,
            skip_if_file_exists=self.skip_if_file_exists,
            keep_project_on_failure=self.keep_project_on_failure,
        )
