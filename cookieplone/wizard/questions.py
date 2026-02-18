# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from cookiecutter.environment import StrictEnvironment

from cookieplone import _types as t
from cookieplone.validators import not_empty
from cookieplone.wizard import prompt


@dataclass
class PromptInfo:
    question: str = ""
    options: tuple[tuple[str, str], ...] = ()


@dataclass
class BaseQuestion:
    key: str
    raw_value: Any

    def default_value(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any]
    ) -> Any:
        default_value = prompt.render_variable(env, self.raw_value, answers)
        return default_value


@dataclass
class HiddenQuestion(BaseQuestion):
    def default_value(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any]
    ) -> Any:
        val = self.raw_value
        if self.key.startswith("__"):
            val = super().default_value(env, answers)
        return val


@dataclass
class Question(BaseQuestion):
    question: PromptInfo
    fieldset: str = "default"
    validator: t.AnswerValidator = not_empty
    prompt_klass: type[prompt.PromptBase] = prompt.Prompt

    def ask(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any], prefix: str = ""
    ) -> Any:
        default_value = self.default_value(env, answers)
        klass = self.prompt_klass
        return klass.ask(f"{prefix}{self.question.question}", default=default_value)


@dataclass
class QuestionBoolean(Question):
    prompt_klass: type[prompt.PromptBase] = prompt.YesNoPrompt

    def ask(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any], prefix: str = ""
    ) -> Any:
        default_value = self.default_value(env, answers)
        klass = self.prompt_klass
        return klass.ask(f"{prefix}{self.question.question}", default=default_value)


@dataclass
class QuestionChoice(Question):
    prompt_klass: type[prompt.Choice] = prompt.Choice

    def default_value(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any]
    ) -> Any:
        default_value = super().default_value(env, answers)
        return default_value[0] if default_value else ""

    def options(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any]
    ) -> tuple[tuple[str, str], ...]:
        options = []
        for opt, title in self.question.options:
            options.append((prompt.render_variable(env, opt, answers), title))
        return tuple(options)

    def ask(
        self, env: StrictEnvironment, answers: OrderedDict[str, Any], prefix: str = ""
    ) -> Any:
        options = self.options(env, answers)
        title = self.question.question
        klass = self.prompt_klass
        return klass.ask(f"{prefix}{title}", choices=options, default="1")
