from pathlib import Path

import pytest

STRUCTURE = [
    "templates",
    "templates/add-ons/backend",
    "templates/add-ons/frontend",
    "templates/add-ons/monorepo",
    "templates/add-ons/seven_addon",
    "templates/agents/instructions",
    "templates/ci/gh_backend_addon",
    "templates/ci/gh_classic_project",
    "templates/ci/gh_frontend_addon",
    "templates/ci/gh_monorepo_addon",
    "templates/ci/gh_project",
    "templates/devops/ansible",
    "templates/docs/starter",
    "templates/ide/vscode",
    "templates/projects/classic",
    "templates/projects/monorepo",
    "templates/sub/addon_settings",
    "templates/sub/cache",
    "templates/sub/classic_project_settings",
    "templates/sub/frontend_project",
    "templates/sub/project_settings",
]


@pytest.fixture(scope="session")
def repository_structure(tmpdir_factory):
    tmp_path = Path(tmpdir_factory.mktemp("repository_structure"))
    for folder in STRUCTURE:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture(scope="session")
def get_path(repository_structure):
    def func(sub_path: str) -> Path:
        return (repository_structure / sub_path).resolve()

    return func
