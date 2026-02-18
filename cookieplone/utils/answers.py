import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

from cookieplone.settings import CONFIG_COMPUTED_KEYS


def remove_internal_keys(raw_answers: OrderedDict[str, Any]) -> dict:
    """Remove internal and computed keys.

    Keep only those defined in CONFIG_COMPUTED_KEYS,
    which are needed for subtemplate generation.
    """
    new_context = {}
    for key, value in raw_answers.items():
        if key.startswith("_") and key not in CONFIG_COMPUTED_KEYS:
            continue
        new_context[key] = value
    return new_context


def write_answers(raw_answers: OrderedDict[str, Any], template_name: str) -> Path:
    file_name = raw_answers.get("_folder_name", template_name)
    answers = remove_internal_keys(raw_answers)
    path = Path(f".cookieplone_answers_{file_name}.json")
    answers["__template__"] = template_name
    with path.open("w") as f:
        json.dump(answers, f, indent=2)
    return path
