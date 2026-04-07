from collections import OrderedDict
from cookieplone.config import Answers
from cookieplone.settings import CONFIG_COMPUTED_KEYS
from cookieplone.utils import files
from copy import deepcopy
from pathlib import Path
from typing import Any


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


def write_answers(
    wizard_answers: Answers, template_name: str, no_input: bool = False
) -> Path:
    """Persist answers to a local JSON file for replay or inspection.

    The source of answers depends on whether the run was interactive:

    * **Interactive** (``no_input=False``): ``wizard_answers.user_answers``
      is written — the values explicitly entered or confirmed by the user
      through the wizard.
    * **Non-interactive** (``no_input=True``): the wizard is never shown, so
      ``user_answers`` is empty.  ``wizard_answers.initial_answers`` is
      written instead — the pre-populated, user-facing values derived from the
      user config, extra context, or replay file.

    In both cases the file is created in the current working directory and
    named after the generated folder (``_folder_name`` answer key), falling
    back to *template_name*.

    :param wizard_answers: The :class:`~cookieplone.config.state.Answers`
        instance produced by the run.
    :param template_name: Fallback stem for the output filename when the
        answers do not contain a ``_folder_name`` key.
    :param no_input: When ``True`` the wizard was skipped; persist
        ``initial_answers`` rather than ``user_answers``.
    :returns: Path to the written JSON file.
    """
    answers = wizard_answers.answers
    user_answers = wizard_answers.user_answers
    initial_answers = wizard_answers.initial_answers
    persisted_answers = deepcopy(initial_answers if no_input else user_answers)
    # Record the template name on the persisted copy so that the file can be
    # replayed (or fed to ``--answers-file``) without having to specify the
    # template again on the CLI.
    persisted_answers["__template__"] = template_name
    file_name = answers.get("_folder_name", template_name)
    path = Path(f".cookieplone_answers_{file_name}.json")
    return files.save_json(path, persisted_answers)
