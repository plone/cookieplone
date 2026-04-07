"""Helpers for post-generation hooks that orchestrate sub-template rendering."""

import logging
from collections import OrderedDict
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

from cookieplone.config import CookieploneState
from cookieplone.settings import TEMPLATES_FOLDER
from cookieplone.utils.console import print as console_print
from cookieplone.utils.console import quiet_mode
from cookieplone.utils.cookiecutter import create_jinja_env

logger = logging.getLogger(__name__)

#: Signature for custom subtemplate handler functions.
#: Receives ``(context, output_dir)`` and returns the generated directory path.
SubtemplateHandler = Callable[[OrderedDict, Path], Path]


def process_subtemplates(
    state: CookieploneState, data: dict[str, Any]
) -> list[list[str]]:
    """Convert v2 subtemplates into the v1 tuple format for post-gen hooks.

    Post-generation hooks expect ``__cookieplone_subtemplates`` as a list of
    ``[id, title, enabled]`` lists.  The ``enabled`` value may be a Jinja2
    expression (e.g. ``"{{ cookiecutter.has_frontend }}"``), so it is rendered
    against the current context before being returned.

    :param state: Current run state containing the parsed subtemplates.
    :param data: The cookiecutter context dict (inner dict, not the wrapper).
    :returns: A list of ``[id, title, enabled]`` lists ready for injection.
    """
    subtemplates = state.subtemplates or []
    env = create_jinja_env(data)
    return [
        [s["id"], s["title"], env.from_string(s["enabled"]).render()]
        for s in subtemplates
    ]


def _parse_subtemplate_entry(
    entry: list | dict,
) -> dict[str, str]:
    """Normalise a single subtemplate entry into a dict.

    Supports both legacy tuple/list format ``[id, title, enabled]`` and the
    new dict format ``{"id": ..., "title": ..., "enabled": ..., "folder_name": ...}``.

    :param entry: A subtemplate entry in either format.
    :returns: A dict with keys ``id``, ``title``, ``enabled``, and ``folder_name``.
    :raises ValueError: If the entry format is not recognized.
    """
    if isinstance(entry, dict):
        result = {
            "id": entry["id"],
            "title": entry["title"],
            "enabled": entry["enabled"],
            "folder_name": entry.get("folder_name", ""),
        }
    elif isinstance(entry, (list, tuple)) and len(entry) >= 3:
        result = {
            "id": entry[0],
            "title": entry[1],
            "enabled": entry[2],
            "folder_name": entry[3] if len(entry) > 3 else "",
        }
    else:
        raise ValueError(f"Unrecognized subtemplate entry format: {entry!r}")
    return result


def run_subtemplates(
    context: OrderedDict,
    output_dir: Path,
    handlers: dict[str, SubtemplateHandler] | None = None,
) -> dict[str, Path]:
    """Process and generate all subtemplates defined in the context.

    This is the main entry point for post-generation hooks to trigger
    subtemplate generation. It replaces the boilerplate loop that was
    previously duplicated across every ``post_gen_project.py``.

    For each enabled subtemplate:

    - If a matching handler is provided, it is called with a deep copy
      of the context and the output directory.
    - Otherwise, :func:`~cookieplone.generator.generate_subtemplate` is
      called with default arguments.

    Disabled subtemplates are logged and skipped.

    :param context: The cookiecutter context ``OrderedDict`` from the
        post-generation hook.
    :param output_dir: The generated project directory (typically
        ``Path.cwd()``).
    :param handlers: Optional mapping of ``template_id`` →
        :data:`SubtemplateHandler` for subtemplates that need custom
        context manipulation.
    :returns: Dict mapping ``template_id`` → generated ``Path`` for
        each subtemplate that was processed.
    """
    from cookieplone.generator import generate_subtemplate

    if handlers is None:
        handlers = {}

    raw_subtemplates = context.get("__cookieplone_subtemplates", [])
    results: dict[str, Path] = {}

    for entry in raw_subtemplates:
        sub = _parse_subtemplate_entry(entry)
        template_id = sub["id"]
        title = sub["title"]
        enabled = sub["enabled"]
        folder_name = sub["folder_name"]

        if not int(enabled):
            console_print(f" -> Ignoring ({title})")
            continue

        console_print(f" -> {title}")

        # Enter quiet mode for the duration of the dispatch so that nested
        # generate_subtemplate() calls — both from registered handlers and
        # from the default fallback — do not emit their own console output
        # or deprecation warnings while the parent run is active.
        with quiet_mode():
            if template_id in handlers:
                path = handlers[template_id](deepcopy(context), output_dir)
            else:
                # Default generation: resolve folder_name from entry or
                # project dir.
                if folder_name == ".":
                    gen_output_dir = output_dir.parent
                    gen_folder_name = output_dir.name
                elif folder_name:
                    gen_output_dir = output_dir
                    gen_folder_name = folder_name
                else:
                    gen_output_dir = output_dir
                    gen_folder_name = output_dir.name

                template_path = f"{TEMPLATES_FOLDER}/{template_id}"
                path = generate_subtemplate(
                    template_path=template_path,
                    output_dir=gen_output_dir,
                    folder_name=gen_folder_name,
                    context=deepcopy(context),
                )

        results[template_id] = path

    return results
