# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import sys
from datetime import datetime
from pathlib import Path

from cookiecutter import __version__ as __cookiecutter_version__

from cookieplone import __version__, settings
from cookieplone.utils import git

SIGNATURE = (
    "Made with [bold][red]❤️[/red][/bold] by the"
    " [bold][blue]Plone Community[/blue][/bold]"
)


def __cookiecutter_location__() -> Path:
    """Return the cookiecutter location."""
    import cookiecutter

    return Path(cookiecutter.__file__).parent


def __location__() -> Path:
    """Return the cookieplone location."""
    return Path(__file__).parent.parent


def version_info() -> str:
    """Return the Cookieplone version, location and Python powering it."""
    python_version = sys.version
    # Get the root of cookieplone
    return (
        f"Cookieplone {__version__} from {__location__()} "
        f"(Cookiecutter {__cookiecutter_version__}, "
        f"Python {python_version})\n\n"
        f"{SIGNATURE}"
    )


def cookieplone_info(repository: str | Path, passwd: str = "", tag: str = "") -> dict:
    """Print information about current configuration."""
    return {
        "title": "cookieplone",
        "subtitle": SIGNATURE,
        "panels": {
            "cookieplone": {
                "title": "Installation :zap:",
                "rows": [
                    ["Version", __version__],
                    ["Location", f"{__location__()}"],
                ],
            },
            "repository": {
                "title": "Repository :link:",
                "rows": [
                    [f"Location ({settings.REPO_LOCATION})", f"{repository}"],
                    [f"Tag ({settings.REPO_TAG})", tag],
                    [f"Password ({settings.REPO_PASSWORD})", "***" if passwd else ""],
                ],
            },
            "cookiecutter": {
                "title": "Cookiecutter :cookie:",
                "rows": [
                    ["Version", __cookiecutter_version__],
                    ["Location", f"{__cookiecutter_location__()}"],
                ],
            },
            "python": {
                "title": "Python :snake:",
                "rows": [
                    ["Version", f"{sys.version}"],
                ],
            },
        },
    }


def signature_md(path: Path) -> str:
    """Return a signature, in markdown."""
    date_info = f"{datetime.now()}"
    cookieplone = f"[Cookieplone ({__version__})]({settings.COOKIEPLONE_REPO})"
    commit = git.get_last_commit(path)
    template_title = "cookieplone-templates"
    if not commit:
        template_link = settings.TEMPLATES_REPO
    else:
        sha = commit.hexsha
        template_title = f"{template_title} ({sha[:7]})"
        template_link = f"{settings.TEMPLATES_REPO}/commit/{sha}"
    template = f"[{template_title}]({template_link})"
    return f"""Generated using {cookieplone} and {template} on {date_info}"""
