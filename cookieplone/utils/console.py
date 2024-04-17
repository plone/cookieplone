from textwrap import dedent

from rich import print as _print
from rich.markup import escape
from rich.panel import Panel

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
