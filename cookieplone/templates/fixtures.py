from .bake import Cookies
from binaryornot.check import is_binary
from cookieplone.templates import types
from pathlib import Path

import json
import pytest
import re
import yaml


IGNORED_KEYS = (
    "_extensions",
    "_copy_without_render",
    "__prompts__",
    "__cookieplone_subtemplates",
    "__cookieplone_template",
    "__validators__",
    "json",  # Probably `cookiecutter.json`
)

PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r" ?(cookiecutter)[.](?P<key>[a-zA-Z0-9-_]*) ?"),
    re.compile(r"(context\.get\(\")(?P<key>[a-zA-Z0-9-_]*)\""),
)


@pytest.fixture(scope="session")
def variable_pattern() -> tuple[re.Pattern, ...]:
    return PATTERNS


@pytest.fixture(scope="session")
def find_variables(variable_pattern, valid_key) -> types.VariableFinder:
    """Find variables in a string."""

    def func(data: str) -> set:
        keys: set[str] = set()
        for pattern in variable_pattern:
            matches = {match.groupdict()["key"] for match in pattern.finditer(data)}
            matches = {key for key in matches if valid_key(key)}
            keys = keys.union(matches)
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
    """Should we check for this key."""

    def func(key: str, ignore: list[str] | None = None) -> bool:
        ignore = ignore if ignore else IGNORED_KEYS
        return all([
            key not in ignore,
            key.startswith("__") or not key.startswith("_"),
        ])

    return func


def _read_configuration(base_folder: Path) -> dict:
    """Read template configuration from cookieplone.json or cookiecutter.json."""
    v2_file = base_folder / "cookieplone.json"
    v1_file = base_folder / "cookiecutter.json"
    if v2_file.is_file():
        return json.loads(v2_file.read_text())
    return json.loads(v1_file.read_text())


@pytest.fixture
def configuration_data(template_repository_root) -> dict:
    """Return configuration from cookieplone.json or cookiecutter.json."""
    return _read_configuration(template_repository_root)


@pytest.fixture
def sub_templates(configuration_data, template_repository_root) -> list[Path]:
    """Return a list of subtemplates used by this template."""
    templates = []
    parent = Path(template_repository_root).parent
    # v2 format: config.subtemplates as list of {"id", "title", "enabled"}
    config = configuration_data.get("config", {})
    raw_subtemplates = config.get("subtemplates", [])
    if not raw_subtemplates:
        # v1 fallback: flat __cookieplone_subtemplates as list of [id, title, enabled]
        raw_subtemplates = configuration_data.get("__cookieplone_subtemplates", [])
    for sub_template in raw_subtemplates:
        if isinstance(sub_template, dict):
            sub_template_id = sub_template["id"]
        else:
            # v1 tuple/list format
            sub_template_id = sub_template[0]
        sub_template_path = (parent / sub_template_id).resolve()
        if not sub_template_path.exists():
            sub_template_path = Path(parent.parent / sub_template_id).resolve()
        templates.append(sub_template_path)
    return templates


def _get_variable_keys(config_data: dict) -> set[str]:
    """Extract variable keys from a configuration dict (v1 or v2 format)."""
    # v2 format: keys are in schema.properties
    schema = config_data.get("schema", {})
    properties = schema.get("properties", {})
    if properties:
        return set(properties.keys())
    # v1 format: keys are at the top level
    return set(config_data.keys())


@pytest.fixture
def configuration_variables(configuration_data, sub_templates, valid_key) -> set[str]:
    """Return a set of variables available in the template configuration."""
    # Variables
    all_keys = _get_variable_keys(configuration_data)
    variables = {key for key in all_keys if valid_key(key)}
    for sub_template in sub_templates:
        sub_config = _read_configuration(sub_template)
        sub_keys = _get_variable_keys(sub_config)
        variables.update({
            key for key in sub_keys if valid_key(key) and key.startswith("__")
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
        v2_config = base_path / "cookieplone.json"
        v1_config = base_path / "cookiecutter.json"
        if v2_config.is_file():
            all_files.append(v2_config)
        elif v1_config.is_file():
            all_files.append(v1_config)
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


@pytest.fixture(scope="session")
def annotate_context() -> types.ContextAnnotator:
    """Prepare context by adding computed values."""
    from cookieplone.cli import annotate_context

    def func(context: dict, repo_path: Path, template: str) -> dict:
        return annotate_context(context, repo_path, template)

    return func


@pytest.fixture(scope="session")
def _cookiecutter_config_file(tmpdir_factory):
    user_dir = tmpdir_factory.mktemp("user_dir")
    config_file = user_dir.join("config")

    config = {
        "cookiecutters_dir": str(user_dir.mkdir("cookiecutters")),
        "replay_dir": str(user_dir.mkdir("cookiecutter_replay")),
    }

    with config_file.open("w", encoding="utf-8") as f:
        yaml.dump(config, f, Dumper=yaml.Dumper)

    return config_file


@pytest.fixture
def cookies(request, tmpdir, _cookiecutter_config_file):
    """Yield an instance of the Cookies helper class that can be used to
    generate a project from a template.

    Run cookiecutter:
        result = cookies.bake(extra_context={
            'variable1': 'value1',
            'variable2': 'value2',
        })
    """
    template_dir = request.config.option.template

    output_dir = tmpdir.mkdir("cookies")
    output_factory = output_dir.mkdir

    yield Cookies(template_dir, output_factory, _cookiecutter_config_file)

    # Add option to keep generated output directories.
    if not request.config.option.keep_baked_projects:
        output_dir.remove()


@pytest.fixture(scope="module")
def cookies_module(request, tmpdir_factory, _cookiecutter_config_file):
    """Yield an instance of the Cookies helper class that can be used to
    generate a project from a template.

    Run cookiecutter:
        result = cookies.bake(extra_context={
            'variable1': 'value1',
            'variable2': 'value2',
        })
    """
    template_dir = request.config.option.template

    output_dir = tmpdir_factory.mktemp("cookies")
    output_factory = output_dir.mkdir

    yield Cookies(template_dir, output_factory, _cookiecutter_config_file)

    # Add option to keep generated output directories.
    if not request.config.option.keep_baked_projects:
        output_dir.remove()


@pytest.fixture(scope="session")
def cookies_session(request, tmpdir_factory, _cookiecutter_config_file):
    """Yield an instance of the Cookies helper class that can be used to
    generate a project from a template.

    Run cookiecutter:
        result = cookies.bake(extra_context={
            'variable1': 'value1',
            'variable2': 'value2',
        })
    """
    template_dir = request.config.option.template

    output_dir = tmpdir_factory.mktemp("cookies")
    output_factory = output_dir.mkdir

    yield Cookies(template_dir, output_factory, _cookiecutter_config_file)

    # Add option to keep generated output directories.
    if not request.config.option.keep_baked_projects:
        output_dir.remove()


def pytest_addoption(parser):
    group = parser.getgroup("cookies")
    group.addoption(
        "--template",
        action="store",
        default=".",
        dest="template",
        help="specify the template to be rendered",
        type=str,
    )

    group.addoption(
        "--keep-baked-projects",
        action="store_true",
        default=False,
        dest="keep_baked_projects",
        help="Keep projects directories generated with 'cookies.bake()'.",
    )


def pytest_configure(config):
    # To protect ourselves from tests or fixtures changing directories, keep
    # an absolute path to the template.
    config.option.template = Path(config.option.template).resolve()
