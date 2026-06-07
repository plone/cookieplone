from cookieplone import _types as t
from cookieplone.config.state import CookieploneState
from cookieplone.utils import console
from pathlib import Path


def summary_info(state: CookieploneState | None) -> t.SummaryInfo:
    """Resolve the post-generation summary configuration.

    Reads the ``config.summary`` block from the template's
    ``cookieplone-config.json`` (surfaced on
    :attr:`~cookieplone.config.CookieploneState.summary`) and converts it into a
    :class:`~cookieplone._types.SummaryInfo`.  When no summary config is present
    the returned value is disabled by default.

    :param state: The generation state, or ``None`` when unavailable.
    :returns: The resolved :class:`~cookieplone._types.SummaryInfo`.
    """
    raw = state.summary if state else {}
    return t.SummaryInfo.from_dict(raw)


def display_summary_screen(
    path: Path, template_title: str, state: CookieploneState | None
) -> None:
    """Render the post-generation summary screen when it is enabled.

    :param path: Path to the generated project directory.
    :param template_title: Human-readable title of the template that was used.
    :param state: The generation state, or ``None`` when unavailable.
    """
    summary_ = summary_info(state)
    if not summary_.enabled:
        return
    title = "Generation successful"
    if state and state.answers:
        title = state.answers.answers.get("title", title)
    console.summary_screen(
        template_title=template_title,
        title=title,
        path=path,
        info=summary_,
    )
