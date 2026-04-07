"""Validation for the repository-level ``cookieplone-config.json`` format."""

from jsonschema.exceptions import ValidationError
from pathlib import Path
from typing import Any

import json
import jsonschema


_SCHEMA_PATH = Path(__file__).parent / "repository_config.schema.json"
REPOSITORY_CONFIG_SCHEMA: dict[str, Any] = json.loads(_SCHEMA_PATH.read_text())


def _collect_group_errors(data: dict[str, Any]) -> list[str]:
    """Check cross-referential constraints between groups and templates.

    :param data: A repository config dict that has already passed schema
        validation.
    :returns: List of human-readable error messages.  Empty if valid.
    """
    errors: list[str] = []
    template_ids = set(data.get("templates", {}))
    seen: dict[str, str] = {}  # template_id -> group_id

    for group_id, group in data.get("groups", {}).items():
        for tmpl_id in group.get("templates", []):
            if tmpl_id not in template_ids:
                errors.append(
                    f"Group '{group_id}' references template "
                    f"'{tmpl_id}' which is not defined in 'templates'."
                )
            elif tmpl_id in seen:
                errors.append(
                    f"Template '{tmpl_id}' appears in both group "
                    f"'{seen[tmpl_id]}' and group '{group_id}'."
                )
            else:
                seen[tmpl_id] = group_id

    # Every template must belong to a group
    ungrouped = template_ids - set(seen)
    for tmpl_id in sorted(ungrouped):
        errors.append(f"Template '{tmpl_id}' is not assigned to any group.")

    return errors


def validate_repository_config(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a repository config dict against the cookieplone-config.json
    schema.

    Performs two levels of validation:

    1. **Structural**: validates the dict against
       :data:`REPOSITORY_CONFIG_SCHEMA` using JSON Schema.
    2. **Cross-referential**: checks that every template referenced by a group
       exists in ``templates``, that no template appears in multiple groups,
       and that every template belongs to at least one group.

    :param data: The repository configuration dict to validate.
    :returns: A ``(valid, errors)`` tuple.  *valid* is ``True`` when no errors
        were found; *errors* is a list of human-readable error messages.
    """
    errors: list[str] = []
    try:
        jsonschema.validate(data, REPOSITORY_CONFIG_SCHEMA)
    except ValidationError as exc:
        errors.append(exc.message)
        return False, errors

    errors.extend(_collect_group_errors(data))
    return len(errors) == 0, errors
