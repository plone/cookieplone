"""JSONSchema definitions for the cookieplone.json v2 configuration format."""

from typing import Any, TypedDict

import jsonschema
from jsonschema.exceptions import ValidationError


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


COOKIEPLONE_CONFIG_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["schema"],
    "properties": {
        "id": {"type": "string"},
        "schema": {
            "type": "object",
            "required": ["version", "properties"],
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string", "const": "2.0"},
                "properties": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "required": ["type", "default"],
                        "properties": {
                            "type": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "default": {},
                            "format": {"type": "string"},
                            "validator": {"type": "string"},
                            "oneOf": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["const", "title"],
                                    "properties": {
                                        "const": {"type": "string"},
                                        "title": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "config": {
            "type": "object",
            "properties": {
                "extensions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "no_render": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "versions": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "subtemplates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "title", "enabled"],
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "enabled": {"type": "string"},
                        },
                    },
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


def validate_cookieplone_config(data: dict[str, Any]) -> bool:
    """Validate a config dict against the cookieplone.json v2 schema.

    :param data: The configuration dict to validate.
    :returns: ``True`` if validation passes, ``False`` otherwise.
    """
    try:
        jsonschema.validate(data, COOKIEPLONE_CONFIG_SCHEMA)
        return True
    except ValidationError:
        return False
