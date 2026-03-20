import pytest

from cookieplone.utils import plone

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
