# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import sys
from datetime import datetime
from pathlib import Path

from cookiecutter import __version__ as __cookiecutter_version__

from cookieplone import __version__
from cookieplone.utils import git

COOKIEPLONE_REPO = "https://github.com/plone/cookieplone"
TEMPLATES_REPO = "https://github.com/plone/cookiecutter-plone"


def version_info() -> str:
    """Return the Cookieplone version, location and Python powering it."""
    python_version = sys.version
    # Get the root of cookieplone
    location = Path(__file__).parent.parent
    return (
        f"Cookieplone {__version__} from {location} "
        f"(Cookiecutter {__cookiecutter_version__}, "
        f"Python {python_version})\n\n"
        f"Made with [bold][red]❤️[/red][/bold] by the"
        " [bold][blue]Plone Community[/blue][/bold]"
    )


def signature_md(path: Path) -> str:
    """Return a signature, in markdown."""
    date_info = f"{datetime.now()}"
    cookieplone = f"[Cookieplone ({__version__})]({COOKIEPLONE_REPO})"
    commit = git.get_last_commit(path)
    if not commit:
        template = f"[cookiecutter-plone]({TEMPLATES_REPO})"
    else:
        sha = commit.hexsha
        template = f"[cookiecutter-plone ({sha[:7]})]({TEMPLATES_REPO}/commit/{sha})"
    return f"""Generated using {cookieplone} and {template} on {date_info}"""
