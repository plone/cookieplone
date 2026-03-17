import os
import sys
from contextlib import contextmanager
from copy import copy
from pathlib import Path

from cookiecutter.replay import load


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
