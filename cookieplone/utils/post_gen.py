"""Helpers for post-generation action hooks.

Provides :func:`run_post_gen_actions` — a single dispatcher that replaces
the boilerplate ``run_actions()`` loop duplicated across every template's
``post_gen_project.py`` — together with a set of ready-made handlers for
common post-generation tasks (git init, file removal, file moves, namespace
packages, ``make format``).
"""

from collections import OrderedDict
from collections.abc import Callable
from cookieplone.utils.console import print as console_print
from cookieplone.utils.files import remove_files
from cookieplone.utils.git import initialize_repository
from cookieplone.utils.plone import (
    create_namespace_packages as _create_namespace_packages,
)
from copy import deepcopy
from pathlib import Path
from typing import TypedDict

import logging
import subprocess


logger = logging.getLogger(__name__)

#: Signature for post-generation action handlers.
#: Receives ``(context, output_dir)`` and returns nothing.
PostGenHandler = Callable[[OrderedDict, Path], None]


class PostGenAction(TypedDict):
    """A single post-generation action entry."""

    handler: PostGenHandler
    title: str
    enabled: bool


def run_post_gen_actions(
    context: OrderedDict,
    output_dir: Path,
    actions: list[PostGenAction],
) -> None:
    """Run a list of post-generation actions against a generated project.

    Each action is a :class:`PostGenAction` dict with *handler*, *title*,
    and *enabled* keys.  Disabled actions are logged and skipped; enabled
    actions receive a deep copy of *context* and the *output_dir*.

    :param context: The cookiecutter context ``OrderedDict`` from the
        post-generation hook.
    :param output_dir: The generated project directory.
    :param actions: Ordered list of actions to execute.
    """
    for action in actions:
        title = action["title"]
        enabled = action["enabled"]
        handler = action["handler"]

        if not int(enabled):
            console_print(f" -> Ignoring ({title})")
            continue

        console_print(f" -> {title}")
        handler(deepcopy(context), output_dir)


# ---------------------------------------------------------------------------
# Built-in handlers
# ---------------------------------------------------------------------------


def initialize_git_repository(context: OrderedDict, output_dir: Path) -> None:
    """Initialize a git repository in *output_dir* and stage all files.

    Wraps :func:`~cookieplone.utils.git.initialize_repository`.  After the
    initial ``git add`` performed by that function, a second ``git add`` is
    run to capture any files created by earlier post-gen actions.
    """
    repo = initialize_repository(output_dir)
    repo.git.add(output_dir)


def create_namespace_packages(context: OrderedDict, output_dir: Path) -> None:
    """Create Python namespace package structure.

    Reads ``python_package_name`` from *context* and delegates to
    :func:`~cookieplone.utils.plone.create_namespace_packages`.  The
    ``namespace_style`` key defaults to ``"native"`` (PEP 420).
    """
    package_name = context.get("python_package_name", "")
    if not package_name or "." not in package_name:
        return
    style = context.get("namespace_style", "native")
    _create_namespace_packages(output_dir, package_name, style)


def remove_files_by_key(
    to_remove: dict[str, list[str]],
    key: str,
) -> PostGenHandler:
    """Return a handler that removes files listed under *key* in *to_remove*.

    :param to_remove: Mapping of group keys to lists of relative paths.
    :param key: The group to remove.
    :returns: A :data:`PostGenHandler` suitable for :class:`PostGenAction`.

    Example::

        POST_GEN_TO_REMOVE = {
            "devops-ansible": ["devops/ansible"],
            "devops-gha": [".github/workflows/deploy.yml"],
        }
        action = {
            "handler": remove_files_by_key(POST_GEN_TO_REMOVE, "devops-ansible"),
            "title": "Remove Ansible files",
            "enabled": True,
        }
    """

    def _handler(context: OrderedDict, output_dir: Path) -> None:
        paths = to_remove.get(key, [])
        if paths:
            remove_files(output_dir, paths)

    return _handler


def move_files(
    pairs: list[tuple[str, str]],
) -> PostGenHandler:
    """Return a handler that renames files within *output_dir*.

    :param pairs: List of ``(source, destination)`` relative paths.
    :returns: A :data:`PostGenHandler` suitable for :class:`PostGenAction`.

    Example::

        action = {
            "handler": move_files([("docs/.readthedocs.yaml", ".readthedocs.yml")]),
            "title": "Move docs config",
            "enabled": True,
        }
    """

    def _handler(context: OrderedDict, output_dir: Path) -> None:
        for src, dst in pairs:
            src_path = output_dir / src
            dst_path = output_dir / dst
            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                src_path.rename(dst_path)
            else:
                logger.warning(
                    f"move_files: source {src_path} does not exist, skipping"
                )

    return _handler


def run_make_format(
    make_target: str = "format",
    folder: str = "",
) -> PostGenHandler:
    """Return a handler that runs ``make <target>`` in a subfolder.

    :param make_target: The make target to invoke (default ``"format"``).
    :param folder: Subfolder relative to *output_dir*.  When empty, runs
        in *output_dir* itself.
    :returns: A :data:`PostGenHandler` suitable for :class:`PostGenAction`.

    Example::

        action = {
            "handler": run_make_format("format", "backend"),
            "title": "Format backend code",
            "enabled": True,
        }
    """

    def _handler(context: OrderedDict, output_dir: Path) -> None:
        cwd = output_dir / folder if folder else output_dir
        if not (cwd / "Makefile").exists():
            logger.warning(f"run_make_format: no Makefile in {cwd}, skipping")
            return
        subprocess.run(  # noqa: S603
            ["make", make_target],  # noqa: S607
            cwd=cwd,
            capture_output=True,
        )

    return _handler
