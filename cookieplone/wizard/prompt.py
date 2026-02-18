"""Functions for prompting the user for project info."""

from typing import Any

from cookiecutter.environment import StrictEnvironment
from rich.prompt import Confirm, InvalidResponse, PromptBase


class Prompt(PromptBase[str]):
    """A prompt that returns a str."""

    response_type = str


class YesNoPrompt(Confirm):
    """A prompt that returns a boolean for yes/no questions."""

    yes_choices = ("1", "true", "t", "yes", "y", "on")
    no_choices = ("0", "false", "f", "no", "n", "off")

    def process_response(self, value: str) -> bool:
        """Convert choices to a bool."""
        value = value.strip().lower()
        if value in self.yes_choices:
            return True
        elif value in self.no_choices:
            return False
        else:
            raise InvalidResponse(self.validate_error_message)


class Choice(Prompt):
    """A prompt that returns a choice from a list of options."""

    @classmethod
    def ask(
        cls, prompt: str, choices: tuple[tuple[str, str], ...], default: str
    ) -> str:
        """Prompt the user to choose from a list of options."""
        choice_lines = [
            f"    [bold magenta]{idx}[/] - [bold]{value}[/]"
            for idx, (_, value) in enumerate(choices, start=1)
        ]

        full_prompt = "\n".join((
            f"{prompt}",
            "\n".join(choice_lines),
            "    Choose from",
        ))
        user_choice = super().ask(
            full_prompt,
            choices=[str(i) for i in range(1, len(choices) + 1)],
            default=default,
        )
        idx = int(user_choice) - 1
        return choices[idx][0]


def read_user_yes_no(var_name, default_value, question: str, prefix=""):
    """Prompt the user to reply with 'yes' or 'no' (or equivalent values).

    - These input values will be converted to ``True``:
      "1", "true", "t", "yes", "y", "on"
    - These input values will be converted to ``False``:
      "0", "false", "f", "no", "n", "off"

    Actual parsing done by :func:`prompt`; Check this function codebase change in
    case of unexpected behaviour.

    :param str question: Question to the user
    :param default_value: Value that will be returned if no input happens
    """
    return YesNoPrompt.ask(f"{prefix}{question}", default=default_value)


def render_variable(env: StrictEnvironment, raw, answers: dict[str, Any]) -> Any:
    """Render the next variable to be displayed in the user prompt.

    Inside the prompting taken from the cookiecutter.json file, this renders
    the next variable. For example, if a project_name is "Peanut Butter
    Cookie", the repo_name could be be rendered with:

        `{{ cookiecutter.project_name.replace(" ", "_") }}`.

    This is then presented to the user as the default.

    :param Environment env: A Jinja2 Environment object.
    :param raw: The next value to be prompted for by the user.
    :param dict cookiecutter_dict: The current context as it's gradually
        being populated with variables.
    :return: The rendered value for the default variable.
    """
    if raw is None or isinstance(raw, bool):
        return raw

    if isinstance(raw, dict):
        return {
            render_variable(env, k, answers): render_variable(env, v, answers)
            for k, v in raw.items()
        }
    elif isinstance(raw, list):
        return [render_variable(env, v, answers) for v in raw]
    elif not isinstance(raw, str):
        raw = str(raw)

    template = env.from_string(raw)

    return template.render(cookiecutter=answers)
