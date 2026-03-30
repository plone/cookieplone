"""Format used by cookieplone.json files in cookieplone templates.

```json
{
    "title": "Form title",
    "description": "Form description",
    "version": "2.0",
    "properties": {
        "field_name": {
            "type": "string",
            "title": "Question to ask the user",
            "description": "Description of the question",
            "validator": "path.to.validator_function",
            "default": "default value"
        },
        "number": {
            "type": "integer",
            "title": "Enter a number",
            "validator": "path.to.number_validator_function",
            "default": 0
        },
        "other_field_name": {
            "type": "string",
            "oneOf": [
                {"const": "option1", "title": "Option 1 description"},
                {"const": "option2", "title": "Option 2 description"}
            ],
            "title": "Choose an option",
            "validator": "path.to.another_validator_function",
            "default": "option1"
        },
        "a_computed_field": {
            "type": "string",
            "format": "computed",
            "title": "Choose an option",
            "default": "{{ cookiecutter.field_name }}_computed"
        }
    }
}
```
"""

from typing import Any


def parse_v2(context: dict[str, Any]) -> dict[str, Any]:
    """Return the configuration."""
    return context
