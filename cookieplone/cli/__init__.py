# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Main `cookieplone` CLI."""

import os
from copy import deepcopy
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.prompt import Prompt

from cookieplone import _types as t
from cookieplone import data, settings
from cookieplone._types import GenerateConfig
from cookieplone.exceptions import GeneratorException, PreFlightException
from cookieplone.generator import generate
from cookieplone.logger import configure_logger, logger
from cookieplone.repository import (
    get_base_repository,
    get_template_groups,
    get_template_options,
)
from cookieplone.utils import console, files, internal


def validate_extra_context(value: list[str] | None = None) -> list[str]:
    """Validate extra content follows the correct pattern."""
    if not value:
        return []
    for item in value:
        if "=" not in item:
            raise typer.BadParameter(
                f"EXTRA_CONTEXT should contain items of the form key=value; "
                f"'{item}' doesn't match that form"
            )
    return value


def parse_arguments(
    template: str = "", extra_context: list[str] | None = None
) -> tuple[str, list[str]]:
    """Parse cli arguments (`template`, `extra_context`).

    As both arguments have default values, we need to detected when an extra_context is
    parsed by Typer as the template argument.

    :param template: Cli argurment template.
    :param extra_context: Cli argument extra_context (List of string).
    :returns: Tuple with template and extra_context
    """
    extra_context = extra_context if extra_context else []
    if "=" in template:
        # As a template name should not have a `=`, this is
        # actually extra_context being passed in the wrong
        # argument
        extra_context.insert(0, template)
        template = ""
    return template, extra_context


def parse_answers_file(answers_file: Path | None) -> dict[str, Any]:
    """Parse the provided file and return the content as a dictionary."""
    if not answers_file:
        return {}
    try:
        data = files.load_config_file(answers_file)
    except FileNotFoundError as exc:
        console.error(f"Config file {answers_file} does not exist.")
        raise typer.Exit(1) from exc
    else:
        logger.debug(f"Loaded config data from {answers_file}: {data}")
        return data


def parse_extra_context(value: list[str] | None, answers_data: dict[str, Any]) -> dict:
    """Parse extra content and return a dictionary with options."""
    data = deepcopy(answers_data)
    if value:
        # Explicitly overriding provided answers
        data.update(dict([s.split("=") for s in value]))
    return data


def get_password_from_env() -> str:
    """Obtain repository password from environment."""
    variables = [settings.REPO_PASSWORD, "COOKIECUTTER_REPO_PASSWORD"]
    for variable in variables:
        passwd = os.environ.get(variable)
        if passwd:
            return passwd
    return ""


def annotate_context(context: dict, repo_path: Path, template: str) -> dict:
    context["__generator_sha"] = internal.repo_sha(repo_path)
    context["__generator_signature"] = internal.signature_md(repo_path)
    context["__cookieplone_repository_path"] = f"{repo_path}"
    context["__cookieplone_template"] = f"{template}"
    return context


def prompt_for_group(
    groups: dict[str, t.CookieploneTemplateGroup],
) -> t.CookieploneTemplateGroup:
    """Display template groups and prompt user to choose one."""
    choices = {f"{idx}": name for idx, name in enumerate(groups, 1)}
    console.welcome_screen(groups=groups)
    answer = Prompt.ask("Select a category", choices=list(choices.keys()), default="1")
    return groups[choices[answer]]


def prompt_for_template(base_path: Path, all_: bool = False) -> t.CookieploneTemplate:
    """Parse config in base_path and prompt user to choose a template.

    When the repository defines groups, a two-step selection is presented:
    first the user picks a category, then a template within that category.
    Otherwise the flat template list is shown directly.
    """
    groups = get_template_groups(base_path, all_)
    if groups:
        group = prompt_for_group(groups)
        console.clear_screen()
        templates = group.templates
    else:
        templates = get_template_options(base_path, all_)
    choices = {f"{idx}": name for idx, name in enumerate(templates, 1)}
    console.welcome_screen(templates=templates)
    answer = Prompt.ask("Select a template", choices=list(choices.keys()), default="1")
    console.clear_screen()
    return templates[choices[answer]]


def get_template(template: str, repo_path: Path, all_: bool) -> t.CookieploneTemplate:
    if not template:
        # Display template options
        cookieplone_template = prompt_for_template(repo_path, all_)
    else:
        # Template name was passed from command line
        # so we get all template options, including the hidden ones
        templates = get_template_options(repo_path, True)
        cookieplone_template = templates.get(template)
        if not cookieplone_template:
            console.error(
                f"We do not have a template named {template}.\n"
                f"Available templates are: {', '.join(templates.keys())}\n"
                "Exiting now."
            )
            raise typer.Exit(1)
        console.welcome_screen()
    return cookieplone_template


def cli(
    template: Annotated[str, typer.Argument(help="Template to be used.")] = "",
    extra_context: Annotated[
        data.OptionalListStr,
        typer.Argument(callback=validate_extra_context, help="Extra context."),
    ] = None,
    output_dir: Annotated[
        data.OptionalPath,
        typer.Option("--output-dir", "-o", help="Where to generate the code."),
    ] = None,
    tag: Annotated[
        str, typer.Option("--tag", "--branch", help="Tag.")
    ] = settings.REPO_DEFAULT_TAG,
    info: Annotated[
        bool,
        typer.Option(
            "--info", help="Display information about cookieplone installation."
        ),
    ] = False,
    version: Annotated[
        bool, typer.Option("--version", help="Display the version of cookieplone.")
    ] = False,
    no_input: Annotated[
        bool,
        typer.Option(
            "--no-input",
            help=(
                "Do not prompt for parameters and only use cookiecutter.json "
                "file content. Defaults to deleting any cached resources and "
                "redownloading them. Cannot be combined with the --replay flag."
            ),
        ),
    ] = False,
    replay: Annotated[bool, typer.Option("--replay", "-r")] = False,
    replay_file: Annotated[data.OptionalPath, typer.Option("--replay-file")] = None,
    skip_if_file_exists: Annotated[
        bool,
        typer.Option(
            "--skip-if-file-exists",
            "-s",
            help=(
                "Skip the files in the corresponding directories if they already exist"
            ),
        ),
    ] = False,
    overwrite_if_exists: Annotated[
        bool, typer.Option("--overwrite-if-exists", "-f")
    ] = False,
    answers_file: Annotated[
        data.OptionalPath,
        typer.Option(
            "--answers-file", "--answers", help="Answers file to load default values."
        ),
    ] = None,
    config_file: Annotated[
        data.OptionalPath, typer.Option("--config-file", help="User configuration file")
    ] = None,
    default_config: Annotated[
        bool,
        typer.Option(
            "--default-config",
            help="Do not load a config file. Use the defaults instead",
        ),
    ] = False,
    keep_project_on_failure: Annotated[
        bool,
        typer.Option(
            "--keep-project-on-failure", help="Do not delete project folder on failure"
        ),
    ] = False,
    debug_file: Annotated[
        data.OptionalPath,
        typer.Option(
            "--debug-file", help="File to be used as a stream for DEBUG logging"
        ),
    ] = None,
    all_: Annotated[
        bool,
        typer.Option(
            "--all", "-a", help="Display all templates, including hidden ones"
        ),
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    """Generate a new Plone codebase."""
    if version:
        console.version_screen()
        raise typer.Exit()

    configure_logger(stream_level="DEBUG" if verbose else "INFO", debug_file=debug_file)
    repository = os.environ.get(settings.REPO_LOCATION)
    if not repository:
        repository = settings.REPO_DEFAULT

    passwd = get_password_from_env()
    tag = os.environ.get(settings.REPO_TAG) or tag

    if info:
        console.info_screen(repository=repository, passwd=passwd, tag=tag)
        raise typer.Exit()

    # Process template and extra_context
    template, extra_context = parse_arguments(template, extra_context)

    # Process answers file if provided and update template
    if answers_data := parse_answers_file(answers_file):
        template = answers_data.pop("__template__", template)

    repo_path = get_base_repository(repository, tag)

    # Template info
    cookieplone_template = get_template(template, repo_path, all_)

    if not output_dir:
        output_dir = Path().cwd()

    replay_file = files.resolve_path(replay_file) if replay_file else replay_file
    if replay_file and replay_file.exists():
        # Use replay_file
        replay = replay_file
        extra_context_ = {}
    else:
        # Annotate extra_context
        extra_context_ = annotate_context(
            parse_extra_context(extra_context, answers_data),
            repo_path=repo_path,
            template=cookieplone_template.name,
        )

    # Run generator
    gen_config = GenerateConfig(
        repository=repository,
        template_name=cookieplone_template.name,
        output_dir=output_dir,
        tag=tag,
        no_input=no_input,
        extra_context=extra_context_,
        replay=replay,
        overwrite_if_exists=overwrite_if_exists,
        config_file=config_file,
        default_config=default_config,
        passwd=passwd,
        template_path=str(cookieplone_template.path),
        skip_if_file_exists=skip_if_file_exists,
        keep_project_on_failure=keep_project_on_failure,
    )
    try:
        generate(gen_config)
    except GeneratorException as exc:
        console.error(exc.message)
        raise typer.Exit(1)  # noQA:B904
    except PreFlightException as exc:
        console.error(exc.message)
        raise typer.Exit(1)  # noQA:B904
    except Exception as exc:
        console.error(str(exc))
        raise typer.Exit(1)  # noQA:B904


def main():
    """Run the cli."""
    typer.run(cli)
