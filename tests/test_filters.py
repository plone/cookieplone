import json
from pathlib import Path

import pytest
from cookiecutter.generate import generate_context

from cookieplone.utils.cookiecutter import create_jinja_env


@pytest.fixture
def generate_context_file(tmp_path):
    def func(filter_: str) -> Path:
        # Create cookiecutter.json
        path = tmp_path / "cookiecutter.json"
        context = {"_extensions": [f"cookieplone.filters.{filter_}"]}
        path.write_text(json.dumps(context))
        return path

    return func


@pytest.mark.parametrize(
    "filter_,raw,expected",
    [
        ["package_name", "{{'foo' | package_name}}", "foo"],
        ["package_name", "{{'foo.bar' | package_name}}", "bar"],
        ["package_namespace", "{{'foo' | package_namespace}}", ""],
        ["package_namespace", "{{'foo.bar' | package_namespace}}", "foo"],
        ["package_namespaces", "{{'foo' | package_namespaces}}", ""],
        ["package_namespaces", "{{'foo.bar' | package_namespaces}}", '"foo"'],
        [
            "package_namespaces",
            "{{'foo.bar.baz' | package_namespaces}}",
            '"foo", "foo.bar"',
        ],
        ["package_path", "{{'foo' | package_path}}", "foo"],
        ["package_path", "{{'foo.bar' | package_path}}", "foo/bar"],
        ["package_path", "{{'foo.bar.baz' | package_path}}", "foo/bar/baz"],
        ["pascal_case", "{{'foo_bar' | pascal_case}}", "FooBar"],
        ["use_prerelease_versions", "{{ '' | use_prerelease_versions }}", "No"],
        ["node_version_for_volto", "{{'18' | node_version_for_volto}}", "22"],
        ["node_version_for_volto", "{{'19' | node_version_for_volto}}", "24"],
        ["extract_host", "{{'example.com' | extract_host}}", "example"],
        ["gs_language_code", "{{'ES' | gs_language_code}}", "es"],
        ["gs_language_code", "{{'es-MX' | gs_language_code}}", "es-mx"],
        ["locales_language_code", "{{'es-mx' | locales_language_code}}", "es_MX"],
        ["image_prefix", "{{'github' | image_prefix}}", "ghcr.io/"],
        ["image_prefix", "{{'bitbucket' | image_prefix}}", ""],
        [
            "python_versions",
            "{{'6.0' | python_versions}}",
            "['3.10', '3.11', '3.12']",
        ],
        [
            "python_versions",
            "{{'6.1' | python_versions}}",
            "['3.10', '3.11', '3.12', '3.13']",
        ],
        ["python_version_earliest", "{{'6.0' | python_version_earliest}}", "3.10"],
        ["python_version_earliest", "{{'6.1' | python_version_earliest}}", "3.10"],
        ["python_version_latest", "{{'6.0' | python_version_latest}}", "3.12"],
        ["python_version_latest", "{{'6.1' | python_version_latest}}", "3.13"],
        ["as_semver", "{{'6.1' | as_semver}}", "6.1.0"],
        ["as_semver", "{{'1.0.0a0' | as_semver}}", "1.0.0-alpha.0"],
        [
            "unscoped_package_name",
            "{{'volto-addon' | unscoped_package_name}}",
            "volto-addon",
        ],
        [
            "unscoped_package_name",
            "{{'@plone-collective/volto-addon' | unscoped_package_name}}",
            "volto-addon",
        ],
        [
            "unscoped_package_name",
            "{{'@plone/volto' | unscoped_package_name}}",
            "volto",
        ],
        ["as_major_minor", "{{'1.0.0a0' | as_major_minor}}", "1.0"],
        ["as_major_minor", "{{'6.1.1rc1' | as_major_minor}}", "6.1"],
        ["as_major_minor", "{{'1' | as_major_minor}}", "1.0"],
        ["package_namespace_path", "{{'foo' | package_namespace_path}}", "src/foo"],
        ["package_namespace_path", "{{'foo.bar' | package_namespace_path}}", "src/foo"],
        [
            "package_namespace_path",
            "{{'foo.bar.foobar' | package_namespace_path}}",
            "src/foo",
        ],
        [
            "package_namespace_path",
            "{{'collective.addon' | package_namespace_path}}",
            "src/collective",
        ],
        [
            "package_namespace_path",
            "{{'collective_addon' | package_namespace_path}}",
            "src/collective_addon",
        ],
    ],
)
def test_filters(generate_context_file, filter_: str, raw: str, expected: str):
    path = generate_context_file(filter_)
    context = generate_context(path)
    env = create_jinja_env(context)
    assert env.from_string(raw).render() == expected


@pytest.mark.parametrize(
    "filter_name,template,value,expected_arg",
    [
        ("latest_plone", "{{ true | latest_plone }}", True, True),
        ("latest_plone", "{{ false | latest_plone }}", False, False),
        ("latest_plone", "{{ 'yes' | latest_plone }}", "yes", True),
        ("latest_plone", "{{ 'no' | latest_plone }}", "no", False),
        ("latest_volto", "{{ true | latest_volto }}", True, True),
        ("latest_volto", "{{ false | latest_volto }}", False, False),
        ("latest_volto", "{{ 'yes' | latest_volto }}", "yes", True),
        ("latest_volto", "{{ 'no' | latest_volto }}", "no", False),
    ],
    ids=[
        "latest_plone-bool-true",
        "latest_plone-bool-false",
        "latest_plone-str-yes",
        "latest_plone-str-no",
        "latest_volto-bool-true",
        "latest_volto-bool-false",
        "latest_volto-str-yes",
        "latest_volto-str-no",
    ],
)
def test_version_filters_accept_bool_or_str(
    monkeypatch, generate_context_file, filter_name, template, value, expected_arg
):
    """latest_plone/latest_volto pass the correct bool to the resolver."""
    captured: dict[str, bool] = {}

    def fake_resolver(*, allow_prerelease):
        captured["allow_prerelease"] = allow_prerelease
        return "9.9.9"

    monkeypatch.setattr(f"cookieplone.filters.versions.{filter_name}", fake_resolver)

    path = generate_context_file(filter_name)
    context = generate_context(path)
    env = create_jinja_env(context)
    rendered = env.from_string(template).render()
    assert rendered == "9.9.9"
    assert captured["allow_prerelease"] is expected_arg
