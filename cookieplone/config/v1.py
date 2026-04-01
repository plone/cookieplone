"""Format used by cookiecutter.json files in cookieplone templates.
```json
{
    "field_name": "field_value",
    "number": 1,
    "other_field_name": ["option1", "option2"],
    "_constant": "constant_value",
    "__computed_field": "{{ cookiecutter.field_name }}_computed",
    "__prompts__": {
        "field_name": "Question to ask the user",
        "other_field_name": {
            "__prompt__": "Choose an option",
            "option1": "Option 1 description",
            "option2": "Option 2 description",
        },
    },
    "__validators__": {
        "field_name": "path.to.validator_function",
        "number": "path.to.number_validator_function",
        "other_field_name": "path.to.another_validator_function",
    },
}
```
"""

from typing import Any

from cookieplone.config.v2 import ParsedConfig
from cookieplone.utils.config import convert_v1_to_v2


def parse_v1(context: dict[str, Any]) -> ParsedConfig:
    """Parse configuration from the old format used in cookiecutter.json files."""
    schema: dict[str, Any] = context.get("cookiecutter", context)
    converted = convert_v1_to_v2(schema)
    config = converted.get("config", {})
    return ParsedConfig(
        schema=converted["schema"],
        extensions=config.get("extensions", []),
        no_render=config.get("no_render", []),
        versions=config.get("versions", {}),
        subtemplates=config.get("subtemplates", []),
        template_id=converted.get("id", ""),
    )
