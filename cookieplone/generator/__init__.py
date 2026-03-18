# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

from cookiecutter import exceptions as exc

from cookieplone._types import RunConfig
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


def _dump_answers(answers_: Answers, template_name: str):
    """Dump answers."""
    return answers.write_answers(answers_, template_name)


def generate(
    repository: str | Path,
    tag: str,
    no_input: bool,
    extra_context: dict[str, Any],
    replay: Path | bool,
    overwrite_if_exists: bool,
    output_dir: Path,
    config_file: Path | None,
    default_config,
    passwd,
    template_path,
    skip_if_file_exists,
    keep_project_on_failure,
    template_name: str,
    dump_answers: bool = True,
) -> Path:
    """Generate a project from a cookieplone template.

    Resolves the repository, builds the run state (including any replay or
    extra context), drives the tui-forms wizard, and renders the template
    files via cookiecutter.

    :param repository: URL or local path to the cookieplone/cookiecutter
        template repository.
    :param tag: Git tag or branch to check out.  Pass an empty string to use
        whatever is already checked out locally.
    :param no_input: Skip all prompts and use default/extra context values.
    :param extra_context: Key/value overrides applied on top of template
        defaults.
    :param replay: If ``True`` replay the last run; if a :class:`~pathlib.Path`
        replay from that specific file; if ``False`` run interactively.
    :param overwrite_if_exists: Overwrite the output directory if it already
        exists.
    :param output_dir: Directory in which the generated project is created.
    :param config_file: Path to a user-level cookiecutter config file, or
        ``None`` to use the default.
    :param default_config: If ``True`` use the built-in default config instead
        of reading ``~/.cookiecutterrc``.
    :param passwd: Password for password-protected zip repositories.
    :param template_path: Sub-directory within the repository that contains the
        template.
    :param skip_if_file_exists: Skip files that already exist in the output
        directory instead of overwriting them.
    :param keep_project_on_failure: Do not delete the partially generated
        project if an error occurs.
    :param template_name: Logical name of the template, used for replay file
        naming.
    :param dump_answers: Persist user answers to a local file after generation.
        Set to ``False`` for sub-template calls.
    :returns: Path to the generated project directory.
    :raises exc.InvalidModeException: When incompatible options are combined
        (e.g. *replay* with *no_input* or *extra_context*).
    :raises RepositoryException: When the repository cannot be resolved.
    :raises GeneratorException: For any failure during template rendering.
    """
    if replay and ((no_input is not False) or (extra_context is not None)):
        err_msg = (
            "You can not use both replay and no_input or extra_context "
            "at the same time."
        )
        raise exc.InvalidModeException(err_msg)

    try:
        repository_info = get_repository(
            repository,
            template_name,
            template_path,
            tag,
            no_input,
            True,
            passwd,
            config_file,
            default_config,
        )
    except (RepositoryException, FailedHookException) as e:
        raise RepositoryException() from e
    except PreFlightException as e:
        # Validation check
        raise e

    repo_dir = repository_info.repo_dir

    # Load replay
    replay_dir = repository_info.replay_dir

    context_from_replayfile = load_replay(repo_dir, replay_dir, replay, template_name)

    # Define cookieplone state
    state: CookieploneState = generate_state(
        template_path=repo_dir,
        default_context=repository_info.config_dict["default_context"],
        extra_context=extra_context,
        replay_context=context_from_replayfile if replay else None,
    )

    run_config = RunConfig(
        output_dir=output_dir,
        no_input=no_input,
        accept_hooks=True,
        overwrite_if_exists=overwrite_if_exists,
        skip_if_file_exists=skip_if_file_exists,
        keep_project_on_failure=keep_project_on_failure,
    )
    dump_location = None
    try:
        result = cookieplone(
            state=state,
            repository_info=repository_info,
            run_config=run_config,
        )
        dump_location = result
    except (
        exc.ContextDecodingException,
        exc.OutputDirExistsException,
        exc.InvalidModeException,
        exc.FailedHookException,
        exc.UnknownExtension,
    ) as e:
        raise GeneratorException(message=str(e), state=state, original=e)  # noQA:B904
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
        if dump_answers:
            path = _dump_answers(state.answers, template_name)
            if dump_location:
                # Move file
                path.rename(dump_location / COOKIEPLONE_ANSWERS_FILE)
            cookiecutter.dump_replay(
                state.answers, repository_info.replay_dir, template_name
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
    try:
        result = generate(
            repository,
            "",  # We should have the tag already locally
            True,  # No input
            extra_context,
            False,  # Not running a replay
            True,  # overwrite_if_exists
            output_dir,
            None,  # config_file
            None,  # default_config,
            None,  # password
            template_path,
            False,  # skip_if_file_exists,
            False,  # keep_project_on_failure
            "",  # template_name is not relevant for subtemplates
            dump_answers=False,  # Do not dump answers for subtemplates
        )
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
