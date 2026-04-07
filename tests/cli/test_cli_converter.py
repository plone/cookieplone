from cookieplone.cli.converter import app
from pathlib import Path
from typer.testing import CliRunner

import pytest


runner = CliRunner()

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
]


@pytest.fixture
def prepare_path(template_path, monkeypatch):
    def func(config_file: str) -> Path:
        path = template_path(config_file)
        monkeypatch.chdir(path)
        return path

    return func


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_cli_converter(prepare_path, validate_config, config_file: str):
    path = prepare_path(config_file)
    src = f"{path}/cookiecutter.json"
    dst = f"{path}/cookieplone.json"
    result = runner.invoke(app, [src, dst])
    assert result.exit_code == 0
    # Validate the newly created file
    assert validate_config(dst)


def test_cli_converter_src_not_found(base_template_path, monkeypatch):
    path = base_template_path()
    monkeypatch.chdir(path)
    src = f"{path}/cookiecutter.json"
    dst = f"{path}/cookieplone.json"
    result = runner.invoke(app, [src, dst])
    assert result.exit_code == 1
    assert "Source file" in result.stdout
    assert "cookiecutter.json" in result.stdout
    assert "does not" in result.stdout
