import json
import re
from pathlib import Path

import pytest
from binaryornot.check import is_binary

from . import types


@pytest.fixture(scope="session")
def variable_pattern() -> re.Pattern:
    return re.compile(
        "({{ ?(cookiecutter)[.]([a-zA-Z0-9-_]*)|{%.+(cookiecutter)[.]([a-zA-Z0-9-_]*).+%})"  # noQA: E501
    )


@pytest.fixture(scope="session")
def find_variables(variable_pattern) -> types.VariableFinder:
    """Find variables in a string."""

    def func(data: str) -> set:
        keys = set()
        matches = variable_pattern.findall(data) or []
        for match in matches:
            # Remove empty matches
            match = [item for item in match if item.strip()]
            keys.add(match[-1])
        return keys

    return func


def _as_sorted_list(value: set) -> list:
    """Convert a set to a list and sort it."""
    value = list(value)
    return sorted(value)


@pytest.fixture(scope="session")
def template_repository_root() -> Path:
    """Template root."""
    return Path().cwd().resolve()


@pytest.fixture(scope="session")
def template_folder_name() -> str:
    """Name used for the template folder."""
    return "{{ cookiecutter.__folder_name }}"


@pytest.fixture(scope="session")
def valid_key() -> types.VariableValidator:
    """Check if we will check for this key."""

    def func(key: str, ignore: list[str] | None = None) -> bool:
        ignore = ignore if ignore else ["__prompts__"]
        return all([
            key not in ignore,
            key.startswith("__") or not key.startswith("_"),
        ])

    return func


def _read_configuration(base_folder: Path) -> dict:
    """Read cookiecutter.json."""
    file_ = base_folder / "cookiecutter.json"
    return json.loads(file_.read_text())


@pytest.fixture
def configuration_data(template_repository_root) -> dict:
    """Return configuration from cookiecutter.json."""
    return _read_configuration(template_repository_root)


@pytest.fixture
def sub_templates(configuration_data, template_repository_root) -> list[Path]:
    """Return a list of subtemplates used by this template."""
    templates = []
    parent = template_repository_root.parent
    sub_templates = configuration_data.get("__cookieplone_subtemplates", [])
    for sub_template in sub_templates:
        sub_template_id = sub_template[0]
        sub_template_path = (parent / sub_template_id).resolve()
        if not sub_template_path.exists():
            sub_template_path = (parent.parent / sub_template_id).resolve()
        templates.append(sub_template_path)
    return templates


@pytest.fixture
def configuration_variables(configuration_data, sub_templates, valid_key) -> set[str]:
    """Return a set of variables available in cookiecutter.json."""
    # Variables
    variables = {key for key in configuration_data if valid_key(key)}
    for sub_template in sub_templates:
        sub_config = _read_configuration(sub_template)
        variables.update({
            key for key in sub_config if valid_key(key) and key.startswith("__")
        })
    return variables


def _all_files_in_template(
    base_path: Path, template_folder_name_: str, include_configuration: bool = True
) -> list[Path]:
    """Get all files in a template repository."""
    hooks_folder = base_path / "hooks"
    hooks_files = list(hooks_folder.glob("**/*"))
    template_folder = base_path / template_folder_name_
    project_files = list(template_folder.glob("**/*"))
    all_files = hooks_files + project_files
    if include_configuration:
        all_files.append(base_path / "cookiecutter.json")
    return all_files


@pytest.fixture
def project_variables(
    template_repository_root,
    find_variables,
    configuration_data,
    template_folder_name,
    sub_templates,
) -> set[str]:
    """Return a set with all variables used in the project."""
    base_data = f"{json.dumps(configuration_data)} {template_folder_name}"
    variables = find_variables(base_data)
    all_files = _all_files_in_template(template_repository_root, template_folder_name)
    for sub_template_path in sub_templates:
        all_files.extend(
            _all_files_in_template(sub_template_path, template_folder_name, True)
        )
    for filepath in all_files:
        data = filepath.name
        is_file = filepath.is_file()
        if is_file and not is_binary(f"{filepath}"):
            data = f"{data} {filepath.read_text()}"
        variables.update(find_variables(data))
    return variables


@pytest.fixture
def variables_required() -> set[str]:
    """Variables required to be present, even if not used."""
    return {"__cookieplone_repository_path", "__cookieplone_template"}


@pytest.fixture
def variables_missing(configuration_variables, project_variables) -> list[str]:
    """Return a list of variables used in the project but not in the configuration."""
    return _as_sorted_list(project_variables.difference(configuration_variables))


@pytest.fixture
def variables_not_used(
    configuration_variables, project_variables, variables_required
) -> list[str]:
    """Return a list of variables in the configuration but not used in the project."""
    # Add variables_required
    project_variables.update(variables_required)
    return _as_sorted_list(configuration_variables.difference(project_variables))
