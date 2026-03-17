from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from typing import Any

from cookieplone.config import Answers
from cookieplone.settings import CONFIG_COMPUTED_KEYS
from cookieplone.utils import files


def remove_internal_keys(raw_answers: OrderedDict[str, Any] | dict[str, Any]) -> dict:
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


def write_answers(wizard_answers: Answers, template_name: str) -> Path:
    """Persist user answers to a local JSON file.

    Writes only the user-supplied answers (not computed/internal keys) so
    they can be replayed or inspected after a failed generation run.  The
    file is created in the current working directory and named after the
    generated folder.

    :param wizard_answers: The :class:`~cookieplone.config.state.Answers`
        collected by the wizard.
    :param template_name: Fallback name for the output file when the answers
        do not contain a ``_folder_name`` key.
    :returns: Path to the written JSON file.
    """
    answers = wizard_answers.answers
    user_answers = deepcopy(wizard_answers.user_answers)
    file_name = answers.get("_folder_name", template_name)
    path = Path(f".cookieplone_answers_{file_name}.json")
    user_answers["__template__"] = template_name
    return files.save_json(path, user_answers)
