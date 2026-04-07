# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from .internal import cookieplone_info
from .internal import version_info
from collections.abc import Sequence
from contextlib import contextmanager
from cookieplone import _types as t
from cookieplone.settings import QUIET_MODE_VAR
from pathlib import Path
from rich import print as base_print
from rich.align import Align
from rich.console import Console
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textwrap import dedent

import os


_console = Console()

BANNER = """
          *******
      ***************
    ***             ***
  ***    ***          ***
 ***    *****          ***
***      ***            ***
***               ***   ***
***              *****  ***
***      ***      ***   ***
 ***    *****          ***
  ***    ***          ***
    ***             ***
      ***************
          *******
"""

PLONE_LOGOTYPE_BANNER = """
          *******
      ***************
    ***             ***        *********     ***                                    ***
  ***    ***          ***      ***********   ***                                   * R *
 ***    *****          ***     ***      ***  ***                                    ***
***      ***            ***    ***       *** ***       ****     ***  ***       ****
***               ***   ***    ***      ***  ***     ********   *********    ********
***              *****  ***    ***********   ***    ***    ***  ****   ***  ***    ***
***      ***      ***   ***    *********     ***    ***    ***  ***    ***  **********
 ***    *****          ***     ***           ***    ***    ***  ***    ***  *********
  ***    ***          ***      ***           ****   ***    ***  ***    ***  ***    ...
    ***             ***        ***            *****  ********   ***    ***   ********
      ***************          ***              ***    ****     ***    ***     ****
          *******
"""


def clear_screen():
    """Clear the terminal screen."""
    _console.clear()


def choose_banner() -> str:
    """Based on the terminal width, decide which banner to use."""
    banner = BANNER
    try:
        terminal_size = os.get_terminal_size()
    except OSError:
        return banner
    if terminal_size and terminal_size.columns >= 90:
        banner = PLONE_LOGOTYPE_BANNER
    return banner


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
    banner = choose_banner()
    print(banner, style, color)


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


def create_table(
    columns: list[dict] | None = None,
    rows: Sequence[Sequence[str]] | None = None,
    **kwargs,
) -> Table:
    """Create table."""
    table = Table(**kwargs)
    for column in columns:
        col_title = column.pop("title", "")
        table.add_column(col_title, **column)
    for row in rows:
        table.add_row(*row)
    return table


def styled_list(
    items: list[tuple[str, str]],
) -> Text:
    """Build a styled numbered list from (title, description) pairs."""
    text = Text()
    for idx, (title, description) in enumerate(items, start=1):
        text.append("\n")
        text.append(f" {idx}  ", style="bold cyan")
        text.append(title, style="bold blue")
        text.append(f"\n     {description}", style="dim")
    text.append("\n")
    return text


def list_available_templates(
    templates: dict[str, t.CookieploneTemplate],
) -> Text:
    """Display templates as a styled list."""
    items = [(template.title, template.description) for template in templates.values()]
    return styled_list(items)


def list_available_groups(
    groups: dict[str, t.CookieploneTemplateGroup],
) -> Text:
    """Display template groups as a styled list."""
    items = [(group.title, group.description) for group in groups.values()]
    return styled_list(items)


def welcome_screen(
    templates: dict[str, t.CookieploneTemplate] | None = None,
    groups: dict[str, t.CookieploneTemplateGroup] | None = None,
):
    banner = choose_banner()
    items = [
        Align.center(f"[bold blue]{banner}[/bold blue]"),
    ]
    if groups:
        items.append(
            Panel(list_available_groups(groups), title="Categories", title_align="left")
        )
    elif templates:
        items.append(
            Panel(
                list_available_templates(templates),
                title="Templates",
                title_align="left",
            )
        )
    panel = Panel(
        Group(*items),
        title="cookieplone",
    )
    base_print(panel)


def version_screen():
    """Print version information."""
    base_print(version_info())


def info_screen(repository: str | Path, passwd: str, tag: str):
    info = cookieplone_info(repository, passwd, tag)
    title = info["title"]
    subtitle = info["subtitle"]
    panels = info["panels"]
    columns = [
        {"title": "", "justify": "left", "style": "cyan", "no_wrap": True, "ratio": 1},
        {"title": "", "justify": "left", "style": "cyan", "no_wrap": True, "ratio": 3},
    ]
    items = []
    for panel in panels.values():
        panel_title = panel.get("title")
        panel_rows = panel.get("rows")
        if panel_rows:
            items.append(
                Panel(
                    create_table(
                        columns, panel_rows, expand=True, box=None, show_header=False
                    ),
                    title=panel_title,
                    title_align="left",
                )
            )
    panel = Panel(
        Group(*items),
        title=title,
        subtitle=subtitle,
    )
    base_print(panel)


def enable_quiet_mode():
    """Enable quiet mode."""
    os.environ[QUIET_MODE_VAR] = "1"


def disable_quiet_mode():
    """Disable quiet mode."""
    os.environ.pop(QUIET_MODE_VAR, "")


@contextmanager
def quiet_mode():
    """Context manager that enables quiet mode for the duration of the block.

    Quiet mode is always disabled on exit, even if an exception is raised.
    """
    enable_quiet_mode()
    try:
        yield
    finally:
        disable_quiet_mode()
