from pathlib import Path

import pytest

from cookieplone import _types as t
from cookieplone import repository


@pytest.fixture(scope="session")
def project_source(resources_folder) -> Path:
    path = (resources_folder / "templates_sub_folder").resolve()
    return path


@pytest.mark.parametrize(
    "template_name,title,description,path",
    (
        (
            "project",
            "A Plone Project",
            "Create a new Plone project with backend and frontend components",
            "templates/projects/monorepo",
        ),
        (
            "project_classic",
            "A Plone Classic Project",
            "Create a new Plone Classic project",
            "templates/projects/classic",
        ),
        (
            "backend_addon",
            "Backend Add-on for Plone",
            "Create a new Python package to be used with Plone",
            "templates/addons/backend",
        ),
        (
            "frontend_addon",
            "Frontend Add-on for Plone",
            "Create a new Node package to be used with Volto",
            "templates/addons/frontend",
        ),
        (
            "distribution",
            "A Plone and Volto distribution",
            "Create a new Distribution with Plone and Volto",
            "templates/distributions/monorepo",
        ),
    ),
)
def test_get_template_options(
    project_source, template_name: str, title: str, description: str, path: str
):
    func = repository.get_template_options
    results = func(project_source)
    assert isinstance(results, dict)
    template = results[template_name]
    assert isinstance(template, t.CookieploneTemplate)
    assert template.title == title
    assert template.description == description
    assert isinstance(template.path, Path)
    assert f"{template.path}" == path


@pytest.mark.parametrize(
    "all_,total_templates",
    [
        (False, 5),
        (True, 6),
    ],
)
def test_get_template_options_filter_hidden(
    project_source, all_: bool, total_templates: int
):
    func = repository.get_template_options
    results = func(project_source, all_)
    assert isinstance(results, dict)
    assert len(results) == total_templates
