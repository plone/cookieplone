from cookieplone.utils import plone

import pytest


CONTENT = {
    "packagename": {
        "contents": {
            "__init__.py": "# content\n",
            "foo.py": "# content\n",
            "bar.py": "# content\n",
            "tests": {
                "contents": {
                    "__init__.py": "# content\n",
                    "foo.py": "# content\n",
                    "bar.py": "# content\n",
                }
            },
        }
    }
}


def _create_structure(base, structure):
    for name, value in structure.items():
        if isinstance(value, str):
            (base / name).write_text(value)
        elif isinstance(value, dict) and "contents" in value:
            subdir = base / name
            subdir.mkdir(parents=True, exist_ok=True)
            _create_structure(subdir, value["contents"])


@pytest.fixture
def package_dir(tmp_path):
    """A source directory representing an existing package to be moved."""
    src = tmp_path / "src"
    src.mkdir()
    _create_structure(src, CONTENT)
    return src / "packagename"


def test_create_namespace_packages_native_single_namespace(package_dir):
    """Native style creates the namespace dir without __init__.py."""
    base = package_dir.parent
    plone.create_namespace_packages(package_dir, "collective.mypackage")
    ns_dir = base / "collective"
    assert ns_dir.is_dir()
    assert not (ns_dir / "__init__.py").exists()
    assert (base / "collective" / "mypackage").is_dir()
    assert (base / "collective" / "mypackage" / "__init__.py").exists()


def test_create_namespace_packages_native_deep_namespace(package_dir):
    """Native style creates all namespace dirs for deeply nested packages."""
    base = package_dir.parent
    plone.create_namespace_packages(package_dir, "plone.app.mypackage")
    assert (base / "plone").is_dir()
    assert not (base / "plone" / "__init__.py").exists()
    assert (base / "plone" / "app").is_dir()
    assert not (base / "plone" / "app" / "__init__.py").exists()
    assert (base / "plone" / "app" / "mypackage").is_dir()


def test_create_namespace_packages_pkg_resources_style(package_dir):
    """pkg_resources style writes declare_namespace __init__.py in each namespace dir"""
    base = package_dir.parent
    plone.create_namespace_packages(
        package_dir, "collective.mypackage", style="pkg_resources"
    )
    init_py = base / "collective" / "__init__.py"
    assert init_py.exists()
    assert (
        '__import__("pkg_resources").declare_namespace(__name__)' in init_py.read_text()
    )


def test_create_namespace_packages_pkgutil_style(package_dir):
    """pkgutil style writes extend_path __init__.py in each namespace dir."""
    base = package_dir.parent
    plone.create_namespace_packages(
        package_dir, "collective.mypackage", style="pkgutil"
    )
    init_py = base / "collective" / "__init__.py"
    assert init_py.exists()
    content = init_py.read_text()
    assert "from pkgutil import extend_path" in content
    assert "__path__ = extend_path(__path__, __name__)" in content


def test_create_namespace_packages_pkg_resources_deep_namespace(package_dir):
    """pkg_resources style writes __init__.py in every namespace level."""
    base = package_dir.parent
    plone.create_namespace_packages(
        package_dir, "plone.app.mypackage", style="pkg_resources"
    )
    expected = '__import__("pkg_resources").declare_namespace(__name__)\n'
    assert (base / "plone" / "__init__.py").read_text() == expected
    assert (base / "plone" / "app" / "__init__.py").read_text() == expected


def test_create_namespace_packages_no_namespace(package_dir):
    """Single-level package name produces no namespace dirs, only renames the path."""
    base = package_dir.parent
    plone.create_namespace_packages(package_dir, "mypackage")
    assert (base / "mypackage").is_dir()
    assert not package_dir.exists()


def test_rerun_namespace_package(package_dir):
    """Re-run the same call and make sure it does not break."""
    base = package_dir.parent
    plone.create_namespace_packages(package_dir, "collective.mypackage")
    ns_dir = base / "collective"
    assert ns_dir.is_dir()
    assert (base / "collective" / "mypackage").is_dir()
    assert (base / "collective" / "mypackage" / "__init__.py").exists()
    plone.create_namespace_packages(package_dir, "collective.mypackage")
    ns_dir = base / "collective"
    assert ns_dir.is_dir()
    assert (base / "collective" / "mypackage").is_dir()
    assert (base / "collective" / "mypackage" / "__init__.py").exists()


@pytest.mark.parametrize(
    "package",
    [
        "plone.app.caching",
        "plone.app.dexterity",
        "plone.classicui",
    ],
)
def test_add_package_dependency_to_zcml(read_data_file, package: str):
    src_xml = read_data_file("plone/dependencies.zcml")
    func = plone.add_dependency_to_zcml
    assert package not in src_xml
    zcml_data = func(package, src_xml)
    assert f"""<include package="{package}"/>""" in zcml_data


def test_add_dependency_to_zcml_no_include_key():
    """When there is no <include> element, inject one."""
    raw_xml = (
        '<?xml version="1.0"?>'
        '<configure xmlns="http://namespaces.zope.org/zope">'
        "</configure>"
    )
    result = plone.add_dependency_to_zcml("plone.restapi", raw_xml)
    assert 'package="plone.restapi"' in result


@pytest.mark.parametrize(
    "profile",
    [
        "plone.app.caching:default",
        "plone.volto:default",
    ],
)
def test_add_dependency_profile_to_metadata(read_data_file, profile: str):
    src_xml = read_data_file("plone/metadata.xml")
    func = plone.add_dependency_profile_to_metadata
    assert profile not in src_xml
    xml_data = func(profile, src_xml)
    assert f"""<dependency>profile-{profile}</dependency>""" in xml_data


def test_add_dependency_profile_no_dependencies_key():
    """When <dependencies> element is missing, create it."""
    raw_xml = '<?xml version="1.0"?><metadata><version>1</version></metadata>'
    result = plone.add_dependency_profile_to_metadata(
        "plone.app.caching:default", raw_xml
    )
    assert "<dependency>profile-plone.app.caching:default</dependency>" in result


def test_add_dependency_profile_empty_dependencies():
    """When <dependencies> exists but has no <dependency> child."""
    raw_xml = (
        '<?xml version="1.0"?>'
        "<metadata><version>1</version>"
        "<dependencies></dependencies></metadata>"
    )
    result = plone.add_dependency_profile_to_metadata("plone.volto:default", raw_xml)
    assert "<dependency>profile-plone.volto:default</dependency>" in result


def test_create_namespace_packages_destination_exists(package_dir):
    """When destination already exists, copytree merges and removes source."""
    base = package_dir.parent
    # Pre-create destination with some content
    dest = base / "collective" / "mypackage"
    dest.mkdir(parents=True)
    (dest / "existing.txt").write_text("keep me")
    plone.create_namespace_packages(package_dir, "collective.mypackage")
    assert dest.is_dir()
    # Original content merged
    assert (dest / "__init__.py").exists()
    # Pre-existing content preserved
    assert (dest / "existing.txt").exists()
    # Source removed
    assert not package_dir.exists()


class TestFormatPythonCodebase:
    """Tests for format_python_codebase."""

    def test_no_pyproject_toml(self, tmp_path, caplog):
        """Logs and raises FileNotFoundError when no pyproject.toml."""
        import logging

        with (
            caplog.at_level(logging.INFO, logger="cookieplone"),
            pytest.raises(FileNotFoundError),
        ):
            plone.format_python_codebase(tmp_path)
        assert "No pyproject.toml" in caplog.text

    def test_uses_ruff_formatters(self, tmp_path, monkeypatch):
        """When pyproject.toml contains [tool.ruff], NEW_PY_FORMATTERS are used."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.ruff]\nline-length = 88\n")
        calls = []
        monkeypatch.setattr(
            plone,
            "NEW_PY_FORMATTERS",
            (("ruff_mock", lambda p: calls.append(("ruff_mock", p))),),
        )
        monkeypatch.setattr(
            plone,
            "OLD_PY_FORMATTERS",
            (("old_mock", lambda p: calls.append(("old_mock", p))),),
        )
        plone.format_python_codebase(tmp_path)
        assert len(calls) == 1
        assert calls[0] == ("ruff_mock", tmp_path)

    def test_uses_old_formatters(self, tmp_path, monkeypatch):
        """Without [tool.ruff], OLD_PY_FORMATTERS are used."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.black]\nline-length = 88\n")
        calls = []
        monkeypatch.setattr(
            plone,
            "NEW_PY_FORMATTERS",
            (("ruff_mock", lambda p: calls.append(("ruff_mock", p))),),
        )
        monkeypatch.setattr(
            plone,
            "OLD_PY_FORMATTERS",
            (("old_mock", lambda p: calls.append(("old_mock", p))),),
        )
        plone.format_python_codebase(tmp_path)
        assert len(calls) == 1
        assert calls[0] == ("old_mock", tmp_path)
