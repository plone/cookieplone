from __future__ import annotations

import os
import sys
from contextlib import contextmanager, suppress
from copy import copy
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Environment

from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.replay import dump, load
from cookiecutter.utils import create_env_with_context
from jinja2.exceptions import UndefinedError

from cookieplone.config import Answers
from cookieplone.settings import DEFAULT_DATA_KEY


@contextmanager
def import_patch(repo_dir: Path | str):
    """Temporarily add *repo_dir* to ``sys.path`` for the duration of the block.

    Hooks inside a template repository may import local Python modules that
    are only available within that directory.  This context manager appends
    the directory to ``sys.path`` on entry and restores the original path on
    exit, even if an exception is raised.

    :param repo_dir: Path to the template repository directory.
    """
    current_path = copy(sys.path)
    sys.path.append(str(repo_dir))
    try:
        yield
    finally:
        sys.path = current_path


def load_replay(
    repo_dir: Path, replay_dir: Path, replay: bool | Path, template_name: str
) -> dict:
    """Load a previously recorded replay context.

    :param repo_dir: Path to the template repository (added to ``sys.path``
        so that template hooks can be imported while loading the replay file).
    :param replay_dir: Directory where replay files are stored by default.
    :param replay: If ``True``, load the replay file for *template_name* from
        *replay_dir*.  If a :class:`~pathlib.Path`, treat it as an explicit
        path to a replay file.  If falsy, return an empty dict.
    :param template_name: Name used to locate the replay file when *replay*
        is ``True``.
    :returns: A dict with a ``"cookiecutter"`` key containing the recorded
        answers, or an empty dict when replay is disabled.
    """
    context = {}
    if replay:
        with import_patch(repo_dir):
            if isinstance(replay, bool):
                context = load(replay_dir, template_name)
            else:
                path, template_name = os.path.split(os.path.splitext(replay)[0])
                context = load(path, template_name)
    return context


def dump_replay(answers: Answers, replay_dir: Path, template_name: str) -> None:
    """Dump data to replay this session."""
    context = {DEFAULT_DATA_KEY: answers.answers}
    dump(replay_dir, template_name, context)


def create_jinja_env(context: dict) -> Environment:
    """Create a Jinja2 environment for the given context.

    If *context* does not contain a :data:`~cookieplone.settings.DEFAULT_DATA_KEY`
    key, it is wrapped automatically so that
    :func:`cookiecutter.utils.create_env_with_context` receives the structure
    it expects.  This allows callers to pass either a full cookiecutter context
    or a plain data dict.

    :param context: Template context dict — either a full cookiecutter context
        (``{"cookiecutter": {...}}``) or a plain data dict.
    :returns: A configured :class:`~jinja2.Environment`.
    """
    if DEFAULT_DATA_KEY not in context:
        context = {DEFAULT_DATA_KEY: context}
    env = create_env_with_context(context)
    env.globals.update(context)
    return env


def parse_output_dir_exception(exc_info: OutputDirExistsException) -> str:
    """Parse the output directory from a cookiecutter OutputDirExistsException.

    The exception message typically contains the path to the existing output
    directory, but the format may vary between cookiecutter versions.  This
    function attempts to extract the path from the message for use in error
    reporting and in the GeneratorException.original attribute.

    :param exc_info: The exception instance raised by cookiecutter when the
        output directory already exists.
    :returns: The path to the existing output directory, or a fallback string
        if it cannot be determined.
    """
    message = exc_info.args[0] if exc_info.args else str(exc_info)
    # Attempt to extract the path from the message using known formats
    for part in message.split(" "):
        part = part.strip('"')  # Remove any surrounding quotes
        with suppress(Exception):
            path = Path(part)
            if path.exists():
                return f"'{path}'"
    return ""


def parse_undefined_error(exc_info: UndefinedError, msg: str = "") -> str:
    """Extract the undefined variable name from a Jinja2 :exc:`UndefinedError`.

    Parses the exception message (e.g. ``"'dict object' has no attribute
    '__cookieplone_template'"``) and appends the variable name to *msg* when
    it can be identified.

    :param exc_info: The Jinja2 :exc:`UndefinedError` instance.
    :param msg: Base message to augment with the variable name.
    :returns: *msg* with the variable name appended, or *msg* unchanged if
        the variable name cannot be determined.
    """
    message = exc_info.args[0] if exc_info.args else str(exc_info)
    # "'dict object' has no attribute '__cookieplone_template'"
    parts = message.split(" ")
    key = parts[-1].strip("'")  # Get the last part and remove quotes
    if key.isidentifier():
        return f"{msg}: Variable '{key}' is undefined"
    return msg
