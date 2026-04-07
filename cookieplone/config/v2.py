"""Parser for the cookieplone.json v2 configuration format.

The v2 format separates form schema from generator configuration::

    {
        "id": "project",
        "schema": {
            "title": "Cookieplone Project",
            "description": "",
            "version": "2.0",
            "properties": { ... }
        },
        "config": {
            "extensions": [...],
            "no_render": [...],
            "versions": { ... },
            "subtemplates": [
                {"id": "...", "title": "...", "enabled": "..."}
            ]
        }
    }
"""

from cookieplone.config.schemas import SubTemplate
from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class ParsedConfig:
    """Result of parsing a v2 configuration file.

    :param schema: The form schema dict (``title``, ``description``,
        ``version``, ``properties``).
    :param extensions: Jinja2 extension class paths.
    :param no_render: Glob patterns for files copied without rendering.
    :param versions: Version pinning mapping (e.g. ``{"gha_checkout": "v6"}``).
    :param subtemplates: Sub-template definitions as
        :class:`~cookieplone.config.schemas.SubTemplate` dicts with
        ``id``, ``title``, and ``enabled`` keys.
    :param template_id: The template identifier from the top-level ``id`` field.
    """

    schema: dict[str, Any] = field(default_factory=dict)
    extensions: list[str] = field(default_factory=list)
    no_render: list[str] = field(default_factory=list)
    versions: dict[str, str] = field(default_factory=dict)
    subtemplates: list[SubTemplate] = field(default_factory=list)
    template_id: str = ""


def parse_v2(context: dict[str, Any]) -> ParsedConfig:
    """Parse a v2 configuration dict into schema and config components.

    :param context: The raw v2 configuration dict.
    :returns: A :class:`ParsedConfig` with the schema and config fields separated.
    """
    config = context.get("config", {})
    schema = context.get("schema", context)
    template_id = context.get("id", "")

    return ParsedConfig(
        schema=schema,
        extensions=config.get("extensions", []),
        no_render=config.get("no_render", []),
        versions=config.get("versions", {}),
        subtemplates=config.get("subtemplates", []),
        template_id=template_id,
    )
