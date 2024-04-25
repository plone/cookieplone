# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import os
from textwrap import dedent

from rich import print as base_print
from rich.align import Align
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from cookieplone.settings import QUIET_MODE_VAR

BANNER = """
                 .xxxxxxxxxxxxxx.
             ;xxxxxxxxxxxxxxxxxxxxxx;
          ;xxxxxxxxxxxxxxxxxxxxxxxxxxxx;
        xxxxxxxxxx              xxxxxxxxxx
      xxxxxxxx.                    .xxxxxxxx
     xxxxxxx      xxxxxxx:            xxxxxxx
   :xxxxxx       xxxxxxxxxx             xxxxxx:
  :xxxxx+       xxxxxxxxxxx              +xxxxx:
 .xxxxx.        :xxxxxxxxxx               .xxxxx.
 xxxxx+          ;xxxxxxxx                 +xxxxx
 xxxxx              +xx.                    xxxxx.
xxxxx:                      .xxxxxxxx       :xxxxx
xxxxx                      .xxxxxxxxxx       xxxxx
xxxxx                      xxxxxxxxxxx       xxxxx
xxxxx                      .xxxxxxxxxx       xxxxx
xxxxx:                      .xxxxxxxx       :xxxxx
.xxxxx              ;xx.       ...          xxxxx.
 xxxxx+          :xxxxxxxx                 +xxxxx
 .xxxxx.        :xxxxxxxxxx               .xxxxx.
  :xxxxx+       xxxxxxxxxxx              ;xxxxx:
   :xxxxxx       xxxxxxxxxx             xxxxxx:
     xxxxxxx      xxxxxxx;            xxxxxxx
      xxxxxxxx.                    .xxxxxxxx
        xxxxxxxxxx              xxxxxxxxxx
          ;xxxxxxxxxxxxxxxxxxxxxxxxxxxx+
             ;xxxxxxxxxxxxxxxxxxxxxx;
                 .xxxxxxxxxxxxxx.
"""


def _print(msg: str):
    """Wrapper around rich.print."""
    if not os.environ.get(QUIET_MODE_VAR):
        base_print(msg)


def print(msg: str, style: str = "", color: str = ""):  # noQA:A001
    """Print to console, using style and color.

    style: https://rich.readthedocs.io/en/latest/reference/style.html#rich.style.Style
    """
    tag_open = ""
    tag_close = ""
    markup = " ".join([item.strip() for item in (style, color) if item.strip()])
    if markup:
        tag_open = f"[{markup}]"
        tag_close = f"[/{markup}]"
    _print(f"{tag_open}{escape(msg)}{tag_close}")


def print_plone_banner():
    """Print Plone banner."""
    style: str = "bold"
    color: str = "blue"
    print(BANNER, style, color)


def info(msg: str):
    style: str = "bold"
    color: str = "white"
    print(msg, style, color)


def success(msg: str):
    style: str = "bold"
    color: str = "green"
    print(msg, style, color)


def error(msg: str):
    style: str = "bold"
    color: str = "red"
    print(msg, style, color)


def warning(msg: str):
    style: str = "bold"
    color: str = "yellow"
    print(msg, style, color)


def panel(title: str, msg: str = "", subtitle: str = "", url: str = ""):
    msg = dedent(msg)
    if url:
        msg = f"{msg}\n[link]{url}[/link]"
    _print(
        Panel(
            msg,
            title=title,
            subtitle=subtitle,
        )
    )


def table_available_templates(title: str, rows: list[list[str]]):
    """Display a table of options."""
    table = Table(title=title, expand=True)

    table.add_column("#", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="blue")
    table.add_column("Description", justify="left", style="blue")

    for idx, _, title, description in rows:
        table.add_row(idx, title, description)

    return table


def welcome_screen(templates: list[list[str]] | None = None):
    items = [
        Align.center(f"[bold blue]{BANNER}[/bold blue]"),
    ]
    if templates:
        items.append(Panel(table_available_templates("Templates", templates)))
    panel = Panel(
        Group(*items),
        title="cookieplone",
    )
    base_print(panel)


def enable_quiet_mode():
    """Enable quiet mode."""
    os.environ[QUIET_MODE_VAR] = "1"


def disable_quiet_mode():
    """Disable quiet mode."""
    os.environ.pop(QUIET_MODE_VAR, "")
