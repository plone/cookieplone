# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import json
from collections import OrderedDict
from pathlib import Path

from cookiecutter import exceptions as exc
from cookiecutter.main import cookiecutter

from cookieplone.exceptions import GeneratorException
from cookieplone.utils import console, files


def _remove_internal_keys(context: OrderedDict) -> dict:
    """Remove internal and computed keys."""
    new_context = {
        key: value for key, value in context.items() if not key.startswith("_")
    }
    return new_context


def _get_repository_root(context: OrderedDict, template: str) -> Path:
    """Return the templates root."""
    possible_keys = [
        "__cookieplone_repository_path",
        "_repo_dir",
        "_template",
    ]
    for key in possible_keys:
        repository_path = context.get(key)
        if not repository_path:
            continue
        repository = Path(repository_path).resolve()
        if (repository / template).exists() or (repository.parent / template).exists():
            return repository
    raise exc.RepositoryNotFound()


def generate(
    repository,
    tag,
    no_input,
    extra_context,
    replay,
    overwrite_if_exists,
    output_dir,
    config_file,
    default_config,
    passwd,
    template,
    skip_if_file_exists,
    keep_project_on_failure,
) -> Path:
    try:
        result = cookiecutter(
            f"{repository}",  # cookiecutter expects this to be a string
            tag,
            no_input,
            extra_context=extra_context,
            replay=replay,
            overwrite_if_exists=overwrite_if_exists,
            output_dir=output_dir,
            config_file=config_file,
            default_config=default_config,
            password=passwd,
            directory=template,
            skip_if_file_exists=skip_if_file_exists,
            accept_hooks=True,
            keep_project_on_failure=keep_project_on_failure,
        )
    except (
        exc.ContextDecodingException,
        exc.OutputDirExistsException,
        exc.InvalidModeException,
        exc.FailedHookException,
        exc.UnknownExtension,
        exc.InvalidZipRepository,
        exc.RepositoryNotFound,
        exc.RepositoryCloneFailed,
    ) as e:
        raise GeneratorException(message=str(e), original=e)  # noQA:B904
    except exc.UndefinedVariableInTemplate as undefined_err:
        context_str = json.dumps(undefined_err.context, indent=2, sort_keys=True)
        msg = f"""{undefined_err.message}
        Error message: {undefined_err.error.message}
        Context: {context_str}
        """
        raise GeneratorException(message=msg, original=undefined_err)  # noQA:B904
    except Exception as e:
        raise GeneratorException(message=str(e), original=e)  # noQA:B904
    else:
        return Path(result)


def generate_subtemplate(
    template: str,
    output_dir: Path,
    folder_name: str,
    context: OrderedDict,
    remove_files: list[str] | None = None,
) -> Path:
    # Extract path to repository
    repository = _get_repository_root(context, template)
    # Cleanup context
    extra_context = _remove_internal_keys(context)
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
            None,  # We should have the tag already locally
            True,  # No input
            extra_context,
            False,  # Not running a replay
            True,  # overwrite_if_exists
            output_dir,
            None,  # config_file
            None,  # default_config,
            None,  # password
            template,
            False,  # skip_if_file_exists,
            False,  # keep_project_on_failure
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
