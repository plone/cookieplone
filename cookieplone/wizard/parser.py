# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import importlib
from collections import OrderedDict
from typing import Any

from cookiecutter.environment import StrictEnvironment
from cookiecutter.utils import create_env_with_context

from cookieplone import _types as t
from cookieplone import validators as v
from cookieplone.logger import logger
from cookieplone.wizard import form as f
from cookieplone.wizard import questions as q


def _get_prompt_info(prompts: dict[str, Any], key: str, raw: Any) -> q.PromptInfo:
    prompt_info = q.PromptInfo(question=key, options=())
    raw_prompt = prompts.get(key)
    if raw_prompt is not None:
        if isinstance(raw_prompt, str):
            prompt_info.question = raw_prompt
        elif isinstance(raw_prompt, dict) and isinstance(raw, list):
            prompt_info.question = raw_prompt.pop("__prompt__", key)
            prompt_choices = dict(raw_prompt.items())
            rendered_options: list[str] = raw
            options = tuple([
                (opt, prompt_choices.get(opt, opt)) for opt in rendered_options
            ])
            prompt_info.options = options
    return prompt_info


def _get_validator(validators: dict[str, str], key: str) -> t.AnswerValidator:
    validator_name = validators.get(key)
    validator = v.not_empty
    error_msg = f"Unable to load validator '{validator_name}' for key '{key}'"
    if validator_name is not None:
        mod_name, func_name = validator_name.rsplit(".", 1)
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            logger.debug(error_msg)
        else:
            if (validator_ := getattr(mod, func_name, None)) is None:
                logger.debug(error_msg)
            else:
                validator = validator_
    return validator


def parse_config_v1(
    context: dict[str, Any], no_input: bool = False
) -> f.CookieploneWizard:
    """."""
    env: StrictEnvironment = create_env_with_context(context)
    form_info: dict[str, Any] = context.get("cookiecutter", {})
    prompts = form_info.pop("__prompts__", {})
    validators = form_info.pop("__validators__", {})
    raw_questions = {k: v for k, v in form_info.items() if not k.startswith("_")}
    total = len(raw_questions)
    questions: list[q.Question] = []
    for key, raw_value in raw_questions.items():
        prompt_info = _get_prompt_info(prompts, key, raw_value)
        validator = _get_validator(validators, key)
        if isinstance(raw_value, list):
            # List of options to choose from
            q_type = q.QuestionChoice
        elif isinstance(raw_value, bool):
            # We are dealing with a boolean variable
            q_type = q.QuestionBoolean
        elif not isinstance(raw_value, dict):
            # We are dealing with a regular variable
            q_type = q.Question
        else:
            raise ValueError(f"Unsupported type for key '{key}': {type(raw_value)}")
        questions.append(
            q_type(
                key=key,
                question=prompt_info,
                raw_value=raw_value,
                validator=validator,
            )
        )
    hidden: list[q.HiddenQuestion] = []
    raw_hidden = {k: v for k, v in form_info.items() if k.startswith("_")}
    for key, raw in raw_hidden.items():
        hidden.append(q.HiddenQuestion(key=key, raw_value=raw))
    return f.CookieploneWizard(
        answers=OrderedDict([]),
        questions=tuple(questions),
        hidden=tuple(hidden),
        env=env,
        raw_form=form_info,
        total=total,
        no_input=no_input,
    )
