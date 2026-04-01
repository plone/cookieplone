# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT

import json
from collections import OrderedDict
from pathlib import Path

from cookiecutter import exceptions as exc

from cookieplone._types import GenerateConfig
from cookieplone.config import Answers, CookieploneState, generate_state
from cookieplone.exceptions import (
    FailedHookException,
    GeneratorException,
    PreFlightException,
    RepositoryException,
)
from cookieplone.generator.main import cookieplone
from cookieplone.repository import get_repository
from cookieplone.settings import COOKIEPLONE_ANSWERS_FILE
from cookieplone.utils import answers, console, cookiecutter, files
from cookieplone.utils.cookiecutter import load_replay


def _dump_answers(answers_: Answers, template_name: str, no_input: bool = False):
    """Persist generation answers to a local JSON file via
    :func:`~cookieplone.utils.answers.write_answers`.

    Thin wrapper that forwards *no_input* so the correct answer source is
    selected: ``user_answers`` for interactive runs, ``initial_answers`` when
    the wizard was skipped.

    :param answers_: The :class:`~cookieplone.config.state.Answers` collected
        during the run.
    :param template_name: Fallback stem for the output filename.
    :param no_input: When ``True`` the wizard was skipped; persist
        ``initial_answers`` instead of ``user_answers``.
    :returns: Path to the written JSON file.
    """
    return answers.write_answers(answers_, template_name, no_input)


def generate(config: GenerateConfig) -> Path:
    """Generate a project from a cookieplone template.

    Resolves the repository, builds the run state (including any replay or
    extra context), drives the tui-forms wizard, and renders the template
    files via cookiecutter.

    :param config: A :class:`~cookieplone._types.GenerateConfig` holding all
        generation options.
    :returns: Path to the generated project directory.
    :raises exc.InvalidModeException: When incompatible options are combined
        (e.g. *replay* with *no_input* or *extra_context*).
    :raises RepositoryException: When the repository cannot be resolved.
    :raises GeneratorException: For any failure during template rendering.
    """
    if config.replay and (
        (config.no_input is not False) or (config.extra_context is not None)
    ):
        err_msg = (
            "You can not use both replay and no_input or extra_context "
            "at the same time."
        )
        raise exc.InvalidModeException(err_msg)

    try:
        repository_info = get_repository(
            config.repository,
            config.template_name,
            config.template_path,
            config.tag,
            config.no_input,
            True,
            config.passwd,
            config.config_file,
            config.default_config,
        )
    except (RepositoryException, FailedHookException) as e:
        raise RepositoryException() from e
    except PreFlightException as e:
        # Validation check
        raise e

    repo_dir = repository_info.repo_dir

    # Load replay
    replay_dir = repository_info.replay_dir

    context_from_replayfile = load_replay(
        repo_dir, replay_dir, config.replay, config.template_name
    )

    # Define cookieplone state
    state: CookieploneState = generate_state(
        template_path=repo_dir,
        default_context=repository_info.config_dict["default_context"],
        extra_context=config.extra_context,
        replay_context=context_from_replayfile if config.replay else None,
    )

    run_config = config.to_run_config()
    dump_location = None
    try:
        result = cookieplone(
            state=state,
            repository_info=repository_info,
            run_config=run_config,
        )
        dump_location = result
    except GeneratorException:
        raise
    except exc.UndefinedVariableInTemplate as undefined_err:
        context_str = json.dumps(undefined_err.context, indent=2, sort_keys=True)
        msg = f"""{undefined_err.message}
        Error message: {undefined_err.error.message}
        Context: {context_str}
        """
        raise GeneratorException(message=msg, state=state, original=undefined_err)  # noQA:B904
    except Exception as e:
        raise GeneratorException(message=str(e), state=state, original=e)  # noQA:B904
    else:
        return Path(result)
    finally:
        if config.dump_answers:
            path = _dump_answers(state.answers, config.template_name, config.no_input)
            if dump_location:
                # Move file
                path.rename(dump_location / COOKIEPLONE_ANSWERS_FILE)
            cookiecutter.dump_replay(
                state.answers, repository_info.replay_dir, config.template_name
            )


def generate_subtemplate(
    template_path: str,
    output_dir: Path,
    folder_name: str,
    context: OrderedDict,
    remove_files: list[str] | None = None,
) -> Path:
    """Generate a sub-template as part of a larger cookieplone run.

    Intended to be called from within a cookiecutter hook to render a
    nested template.  Quiet mode is enabled for the duration so that the
    sub-template's output does not clutter the parent run's UI.

    :param template_path: Relative path (within the repository) to the
        sub-template directory.
    :param output_dir: Directory where the sub-template output should be
        written.
    :param folder_name: Name of the folder to create inside *output_dir*.
    :param context: The current cookiecutter context, used to locate the
        repository root and to pass answers through to the sub-template.
    :param remove_files: Optional list of paths relative to the generated
        folder that should be deleted after generation.
    :returns: Path to the generated sub-template directory.
    :raises GeneratorException: If generation of the sub-template fails.
    """
    # Extract path to repository
    repository = files.get_repository_root(context, template_path)
    # Cleanup context
    extra_context = answers.remove_internal_keys(context)
    ## Add folder name again
    extra_context["__folder_name"] = folder_name
    # Enable quiet mode
    console.enable_quiet_mode()
    # Files to be removed
    if remove_files is None:
        remove_files = []
    # Call generate
    config = GenerateConfig(
        repository=repository,
        template_name="",  # Not relevant for subtemplates
        output_dir=output_dir,
        no_input=True,
        extra_context=extra_context,
        overwrite_if_exists=True,
        template_path=template_path,
        dump_answers=False,
    )
    try:
        result = generate(config)
    except GeneratorException as exc:
        console.disable_quiet_mode()
        raise exc
    else:
        console.disable_quiet_mode()
        path = Path(result)
        if remove_files:
            files.remove_files(path, remove_files)
        # Return path
        return path
