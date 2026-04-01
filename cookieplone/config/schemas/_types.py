"""TypedDict definitions for cookieplone configuration structures."""

from typing import TypedDict


class TemplateEntry(TypedDict):
    """A template entry from the repository-level ``templates`` mapping.

    :param path: Relative filesystem path to the template directory
        (e.g. ``"./templates/projects/monorepo"``).
    :param title: Human-readable label shown in the template selection menu.
    :param description: Short description of what the template generates.
    :param hidden: When ``True`` the template is excluded from the default
        menu and only shown with ``--all`` or when invoked by name.
    """

    path: str
    title: str
    description: str
    hidden: bool


class TemplateGroup(TypedDict):
    """A template group from the repository-level ``groups`` mapping.

    :param title: Human-readable label for the group category.
    :param description: Short description of the group's purpose.
    :param templates: Ordered list of template IDs that belong to this group.
        Each ID must match a key in the top-level ``templates`` mapping.
    :param hidden: When ``True`` the group is excluded from the default menu.
    """

    title: str
    description: str
    templates: list[str]
    hidden: bool


class SubTemplate(TypedDict):
    """A sub-template entry from the ``config.subtemplates`` list.

    :param id: Path identifier for the sub-template (e.g. ``"sub/backend"``).
    :param title: Human-readable label shown in logs and hooks.
    :param enabled: Either a static value (``"0"``/``"1"``) or a Jinja2
        expression (e.g. ``"{{ cookiecutter.has_frontend }}"``).
    """

    id: str
    title: str
    enabled: str
