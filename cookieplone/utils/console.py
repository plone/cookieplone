# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from .internal import cookieplone_info
from .internal import version_info
from collections.abc import Sequence
from contextlib import contextmanager
from cookieplone import __version__ as cookieplone_version
from cookieplone import _types as t
from cookieplone import settings
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
from typing import Any

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
    if not os.environ.get(settings.QUIET_MODE_VAR):
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


def print_plone_banner() -> None:
    """Print Plone banner."""
    style: str = "bold"
    color: str = "blue"
    banner = choose_banner()
    print(banner, style, color)


def info(msg: str) -> None:
    """Print an informational message in bold white."""
    style: str = "bold"
    color: str = "white"
    print(msg, style, color)


def success(msg: str) -> None:
    """Print a success message in bold green."""
    style: str = "bold"
    color: str = "green"
    print(msg, style, color)


def error(msg: str) -> None:
    """Print an error message in bold red."""
    style: str = "bold"
    color: str = "red"
    print(msg, style, color)


def warning(msg: str) -> None:
    """Print a warning message in bold yellow."""
    style: str = "bold"
    color: str = "yellow"
    print(msg, style, color)


def panel(title: str, msg: str = "", subtitle: str = "", url: str = "") -> None:
    """Print a Rich panel with an optional subtitle and clickable URL."""
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
    **kwargs: Any,
) -> Table:
    """Create a Rich :class:`~rich.table.Table` from column definitions and row data.

    :param columns: List of dicts, each containing a ``title`` key and any
        extra keyword arguments accepted by :meth:`~rich.table.Table.add_column`.
    :param rows: Sequence of row tuples passed to :meth:`~rich.table.Table.add_row`.
    :param kwargs: Forwarded to the :class:`~rich.table.Table` constructor.
    :returns: A fully populated :class:`~rich.table.Table`.
    """
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


def _render_screen(items: Sequence[Panel | Align], display_banner: bool = True) -> None:
    """Clear the terminal and render a branded cookieplone screen.

    Wraps the provided *items* inside a titled :class:`~rich.panel.Panel`
    with the cookieplone version header and community signature.  When
    *display_banner* is ``True`` the Plone logo is prepended.

    :param items: Rich renderables (typically :class:`~rich.panel.Panel`
        instances) to display inside the outer chrome.
    :param display_banner: When ``True`` (default) prepend the Plone ASCII
        banner above *items*.
    """
    clear_screen()
    if display_banner:
        banner = choose_banner()
        items = [Align.center(f"[bold blue]{banner}[/bold blue]"), *items]
    panel_title = f"cookieplone ({cookieplone_version})"
    panel = Panel(
        Group(*items),
        title=panel_title,
        subtitle=settings.SIGNATURE,
    )
    base_print(panel)


def sanity_screen(msg: str) -> None:
    """Display a full-screen error panel with the Plone banner.

    Used for fatal pre-flight errors (e.g. version gating) that should be
    shown *instead of* the welcome screen.

    :param msg: Plain-text error message.  Rich markup characters are escaped
        automatically.
    """
    styled_msg = f"\n[red]{escape(msg)}[/red]\n"
    items = [
        Panel(styled_msg, title="Error", title_align="left"),
    ]
    _render_screen(items, display_banner=True)


def welcome_screen(
    templates: dict[str, t.CookieploneTemplate] | None = None,
    groups: dict[str, t.CookieploneTemplateGroup] | None = None,
) -> None:
    """Display the Cookieplone welcome screen with an optional template or group list.

    Clears the terminal, renders the Plone banner, and — when provided —
    appends a panel listing either template *groups* (category selection)
    or individual *templates* (template selection).

    :param templates: Templates to list.  Mutually exclusive with *groups*.
    :param groups: Template groups to list.  Takes precedence over *templates*.
    """
    # Always clear the screen, even if we're not printing the banner,
    # to ensure a clean start.
    items = []
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
    _render_screen(items, display_banner=True)


def version_screen() -> None:
    """Print version information."""
    base_print(version_info())


def info_screen(repository: str | Path, passwd: str, tag: str) -> None:
    """Print a detailed information panel about the current Cookieplone installation.

    :param repository: Template repository URL or local path.
    :param passwd: Repository password (may be empty).
    :param tag: Git tag or branch used for the repository.
    """
    info = cookieplone_info(repository, passwd, tag)
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
    _render_screen(items, display_banner=False)


def enable_quiet_mode():
    """Enable quiet mode."""
    os.environ[settings.QUIET_MODE_VAR] = "1"


def disable_quiet_mode():
    """Disable quiet mode."""
    os.environ.pop(settings.QUIET_MODE_VAR, "")


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
