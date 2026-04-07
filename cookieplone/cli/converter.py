# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Converter CLI."""

from cookieplone.utils import config
from cookieplone.utils import console
from pathlib import Path
from typing import Annotated

import typer


app = typer.Typer()


@app.command()
def converter(
    src: Annotated[
        Path, typer.Argument(help="Path to cookiecutter.json file to be converted.")
    ],
    dst: Annotated[
        Path, typer.Argument(help="Path to cookieplone.json file to be created.")
    ],
):
    """Convert a cookiecutter.json file to a cookieplone.json file."""
    if not src.exists():
        console.error(f"Source file {src} does not exist.")
        raise typer.Exit(1)
    output_path = config.cookiecutter_to_cookieplone(src, dst)
    console.success(f"Converted {src} to {output_path}")


def main():  # pragma: no cover
    """Run the cli."""
    app()
