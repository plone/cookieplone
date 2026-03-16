import pytest

from cookieplone.config import CookieploneState
from cookieplone.config import state as config

CONFIG_FILES = [
    "config/v1-agents_instructions.json",
    "config/v1-backend_addon.json",
    "config/v1-ci_gh_backend_addon.json",
    "config/v1-ci_gh_classic_project.json",
    "config/v1-ci_gh_frontend_addon.json",
    "config/v1-ci_gh_monorepo_addon.json",
    "config/v1-ci_gh_project.json",
    "config/v1-classic_project.json",
    "config/v1-devops_ansible.json",
    "config/v1-documentation_starter.json",
    "config/v1-example.json",
    "config/v1-frontend_addon.json",
    "config/v1-ide_vscode.json",
    "config/v1-monorepo_addon.json",
    "config/v1-project.json",
    "config/v1-seven_addon.json",
    "config/v1-sub-addon_settings.json",
    "config/v1-sub-cache.json",
    "config/v1-sub-classic_project_settings.json",
    "config/v1-sub-frontend_project.json",
    "config/v1-sub-project_settings.json",
    "config/v2-sub-project_settings.json",
]


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_generate_state(template_path, config_file: str):
    path = template_path(config_file)
    func = config.generate_state
    result = func(path)
    assert isinstance(result, CookieploneState)
    assert isinstance(result.schema, dict)
    assert isinstance(result.data, dict)
    assert isinstance(result.context, config.Context)
    assert isinstance(result.answers, config.Answers)


@pytest.mark.parametrize(
    "config_file,use_extra,use_replay,len_properties,len_questions,key,default",
    [
        ("config/v1-project.json", False, False, 65, 19, "title", "Project Title"),
        ("config/v1-project.json", True, False, 65, 19, "title", "Titulo"),
        ("config/v1-project.json", True, True, 65, 19, "title", "Other Project"),
    ],
)
def test_generate_state_overrides(
    template_path,
    extra_project,
    replay_project,
    config_file: str,
    use_extra,
    use_replay,
    len_properties,
    len_questions,
    key,
    default,
):
    path = template_path(config_file)
    func = config.generate_state
    payload = {
        "template_path": path,
        "default_context": None,
        "extra_context": extra_project if use_extra else None,
        "replay_context": replay_project if use_replay else None,
    }
    result = func(**payload)
    properties = result.schema.get("properties", {})
    questions = [q for q in properties if not q.startswith("_")]
    assert len(properties) == len_properties
    assert len(questions) == len_questions
    question = properties[key]
    assert question["default"] == default
