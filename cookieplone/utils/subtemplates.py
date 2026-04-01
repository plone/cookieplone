from typing import Any

from cookieplone.config import CookieploneState
from cookieplone.utils.cookiecutter import create_jinja_env


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
