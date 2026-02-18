# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from cookiecutter.environment import StrictEnvironment
from cookiecutter.exceptions import UndefinedVariableInTemplate

from cookieplone.wizard import questions as q


@dataclass
class CookieploneWizard:
    answers: OrderedDict[str, Any]
    questions: tuple[q.Question, ...]
    hidden: tuple[q.HiddenQuestion, ...]
    env: StrictEnvironment
    raw_form: dict[str, Any]
    total: int = 0
    no_input: bool = False

    def _ask_questions(self) -> OrderedDict[str, Any]:
        """Ask the user the questions defined in the form."""
        answers = self.answers
        total = self.total
        env = self.env
        for idx, question in enumerate(self.questions, start=1):
            key = question.key
            payload = [env, answers]
            method = question.default_value
            if not self.no_input:
                method = question.ask
                payload.append(f"[{idx}/{total}] ")
            try:
                answers[key] = method(*payload)
            except UndefinedVariableInTemplate as err:
                msg = f"Unable to render variable '{key}'"
                raise UndefinedVariableInTemplate(msg, err, self.raw_form) from err
        return answers

    def _compute_hidden_fields(
        self, answers: OrderedDict[str, Any]
    ) -> OrderedDict[str, Any]:
        """Compute the hidden fields defined in the form."""
        answers = self.answers
        env = self.env
        for hidden in self.hidden:
            key = hidden.key
            try:
                answers[key] = hidden.default_value(env, answers)
            except UndefinedVariableInTemplate as err:
                msg = f"Unable to render variable '{key}'"
                raise UndefinedVariableInTemplate(msg, err, self.raw_form) from err
        return answers

    def run(self) -> OrderedDict[str, Any]:
        """Run the wizard and return the answers."""
        # Ask questions
        answers = self._ask_questions()
        # Compute hidden fields
        answers = self._compute_hidden_fields(answers)
        return answers
