# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from pathlib import Path
from typing import Any

from cookiecutter import exceptions as exc
from cookiecutter.generate import generate_files

from cookieplone._types import RepositoryInfo, RunConfig
from cookieplone.config import CookieploneState
from cookieplone.exceptions import GeneratorException
from cookieplone.utils.answers import remove_internal_keys
from cookieplone.utils.cookiecutter import import_patch
from cookieplone.wizard import wizard


def _annotate_data(
    data: dict[str, Any],
    run_config: RunConfig,
    repository_info: RepositoryInfo,
) -> None:
    """Inject cookiecutter internal keys into the template context.

    These ``_`` and ``__`` prefixed keys are read by cookiecutter's hook
    runner and file renderer to locate the template, resolve paths, and
    record provenance.  They are written directly into *data* in-place.

    :param data: The mutable context dict for the current template key
        (e.g. ``state.data["cookiecutter"]``).
    :param run_config: Runtime options providing the output directory.
    :param repository_info: Resolved repository paths and metadata.
    """
    # include template dir or url in the context dict
    data["_template"] = str(repository_info.repo_dir)
    data["__cookieplone_repository_path"] = str(repository_info.root_repo_dir)

    # include output_dir in the context dict
    data["_output_dir"] = f"{run_config.output_dir.resolve()}"

    # include repo dir or url in the context dict
    data["_repo_dir"] = f"{repository_info.repo_dir}"

    # include checkout details in the context dict
    data["_checkout"] = repository_info.checkout


def _cookieplone(
    state: CookieploneState,
    repository_info: RepositoryInfo,
    run_config: RunConfig,
) -> Path:
    """Core generation logic: run the wizard then render files.

    :param state: Current run state containing the schema, data, and
        collected answers.
    :param repository_info: Resolved repository paths and metadata.
    :param run_config: Runtime options (output dir, flags, etc.).
    :returns: Path to the generated project directory.
    """
    data = state.data
    default_key = state.root_key

    # Preserve original defaults before the wizard overwrites them
    data[f"_{default_key}"] = remove_internal_keys(data[default_key])
    internal_data = data[default_key]
    # prompt the user to manually configure at the command line.
    # except when 'no-input' flag is set
    with import_patch(repository_info.repo_dir):
        wizard_answers = wizard(
            state, internal_data, run_config.no_input, root_key=default_key
        )
        internal_data.update(wizard_answers.answers)

    _annotate_data(internal_data, run_config, repository_info)
    # Create project from local context and project template.
    with import_patch(repository_info.repo_dir):
        result = generate_files(
            repo_dir=repository_info.repo_dir,
            context=data,
            overwrite_if_exists=run_config.overwrite_if_exists,
            skip_if_file_exists=run_config.skip_if_file_exists,
            output_dir=f"{run_config.output_dir}",
            accept_hooks=run_config.accept_hooks,
            keep_project_on_failure=run_config.keep_project_on_failure,
        )

    return Path(result)


def cookieplone(
    repository_info: RepositoryInfo,
    state: CookieploneState,
    run_config: RunConfig,
) -> Path:
    """Run Cookieplone just as if using it from the command line.

    Wraps :func:`_cookieplone` with structured exception handling, converting
    known cookiecutter exceptions into
    :class:`~cookieplone.exceptions.GeneratorException` so callers receive a
    consistent error type that also carries the run state.

    :param repository_info: Resolved repository paths and metadata.
    :param state: Current run state containing the schema and context.
    :param run_config: Runtime options controlling generation behaviour.
    :returns: Path to the generated project directory.
    :raises GeneratorException: For any cookiecutter-level failure, wrapping
        the original exception and preserving the run state.
    """

    try:
        result = _cookieplone(
            state=state,
            repository_info=repository_info,
            run_config=run_config,
        )
    except (
        exc.ContextDecodingException,
        exc.OutputDirExistsException,
        exc.InvalidModeException,
        exc.FailedHookException,
        exc.UnknownExtension,
    ) as exc_info:
        raise GeneratorException(
            message=str(exc_info), state=state, original=exc_info
        ) from exc_info
    else:
        # Dump file here
        pass

    # Implement cleanup

    return Path(result)
