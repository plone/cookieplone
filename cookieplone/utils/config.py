"""
Version 1 (cookiecutter.json) configuration format.

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

Version 2 (cookieplone.json) configuration format.

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
        }
    }
}
```
"""

from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cookieplone.utils import files


@dataclass
class PromptInfo:
    title: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)


def _get_prompt_info(prompts: dict[str, Any], key: str, raw: Any) -> PromptInfo:
    """Extract prompt information for a given key from the prompts dict."""
    prompt_info = PromptInfo(title=key, options=[])
    raw_prompt = prompts.get(key)
    if raw_prompt is not None:
        if isinstance(raw_prompt, str):
            prompt_info.title = raw_prompt
        elif isinstance(raw_prompt, dict) and isinstance(raw, list):
            if "__prompt__" not in raw_prompt:
                return prompt_info
            prompt_info.title = raw_prompt.pop("__prompt__", key)
            prompt_choices = dict(raw_prompt.items())
            rendered_options: list[str] = raw
            prompt_info.options = [
                (opt, prompt_choices.get(opt, opt)) for opt in rendered_options
            ]
    return prompt_info


def _get_validator(validators: dict[str, str], key: str) -> str:
    """Get the validator function for a given key."""
    validator_name = validators.get(key)
    return validator_name if validator_name is not None else ""


def _convert_subtemplates(
    raw_subtemplates: list[Any],
) -> list[dict[str, str]]:
    """Convert v1 subtemplate tuples ``[id, title, enabled]`` to dicts."""
    subtemplates: list[dict[str, str]] = []
    for entry in raw_subtemplates:
        if isinstance(entry, (list, tuple)) and len(entry) >= 3:
            subtemplates.append({
                "id": entry[0],
                "title": entry[1],
                "enabled": entry[2],
            })
    return subtemplates


def _convert_property(
    key: str,
    raw_value: Any,
    prompts: dict[str, Any],
    validators: dict[str, str],
) -> dict[str, Any]:
    """Convert a single v1 property to a v2 property definition."""
    prompt_info = _get_prompt_info(prompts, key, raw_value)
    validator = _get_validator(validators, key)
    prop: dict[str, Any] = {
        "type": "string",
        "title": prompt_info.title,
        "default": raw_value,
        "validator": validator,
    }
    if key.startswith("__"):
        prop["format"] = "computed"
    elif key.startswith("_"):
        prop["format"] = "constant"
    elif isinstance(raw_value, list):
        prop["default"] = raw_value[0] if raw_value else raw_value
        prop["oneOf"] = [
            {"const": value, "title": label} for value, label in prompt_info.options
        ]
    elif isinstance(raw_value, bool):
        prop["type"] = "boolean"
    elif isinstance(raw_value, int):
        prop["type"] = "integer"
    elif isinstance(raw_value, str):
        prop["type"] = "string"
    else:
        raise ValueError(f"Unsupported type for key '{key}': {type(raw_value)}")
    return prop


def convert_v1_to_v2(src: dict[str, Any]) -> dict[str, Any]:
    """Convert a version 1 config dict to a version 2 config dict.

    Extracts generator configuration keys (``_extensions``,
    ``_copy_without_render``, ``__cookieplone_subtemplates``,
    ``__cookieplone_template``) from the flat v1 properties into a
    separate ``config`` section and wraps the remaining fields under
    ``schema``.
    """
    data: dict[str, Any] = src.get("cookiecutter", src.copy())
    data = dict(data)
    prompts = data.pop("__prompts__", {})
    validators = data.pop("__validators__", {})

    # Extract config keys before iterating properties
    extensions = data.pop("_extensions", [])
    no_render = data.pop("_copy_without_render", [])
    template_id = data.pop("__cookieplone_template", "")
    subtemplates = _convert_subtemplates(data.pop("__cookieplone_subtemplates", []))

    properties: OrderedDict[str, Any] = OrderedDict()
    for key, raw_value in data.items():
        properties[key] = _convert_property(key, raw_value, prompts, validators)

    config: dict[str, Any] = {}
    if extensions:
        config["extensions"] = extensions
    if no_render:
        config["no_render"] = no_render
    if subtemplates:
        config["subtemplates"] = subtemplates

    result: dict[str, Any] = {}
    if template_id:
        result["id"] = template_id
    result["schema"] = {
        "title": "Cookieplone",
        "description": "",
        "version": "2.0",
        "properties": properties,
    }
    if config:
        result["config"] = config
    return result


def cookiecutter_to_cookieplone(src: Path, dst: Path) -> Path:
    """Convert a cookiecutter.json file to a cookieplone.json file."""
    config = files.load_json(src)
    converted = convert_v1_to_v2(config)
    return files.save_json(dst, converted)


def validate_config(config: dict[str, Any]) -> bool:
    """Validate the config against the cookieplone v2 JSONSchema."""
    from cookieplone.config.schemas import validate_cookieplone_config

    return validate_cookieplone_config(config)
