import os
import sys
from contextlib import contextmanager, suppress
from copy import copy
from pathlib import Path

from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.replay import dump, load

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
    yield
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
