"""Validation for the per-template ``cookieplone.json`` v2 format."""

from jsonschema.exceptions import ValidationError
from pathlib import Path
from typing import Any

import json
import jsonschema


_SCHEMA_PATH = Path(__file__).parent / "cookieplone_config.schema.json"
COOKIEPLONE_CONFIG_SCHEMA: dict[str, Any] = json.loads(_SCHEMA_PATH.read_text())


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
