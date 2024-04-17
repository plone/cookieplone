import pytest

from cookieplone.utils import validators


@pytest.mark.parametrize(
    "key,value,expected",
    [
        ["foo", "", "foo should be provided"],
        ["foo", "not empty", ""],
    ],
)
def test_validate_not_empty(key: str, value: str, expected: str):
    func = validators.validate_not_empty
    assert func(key, value) == expected


@pytest.mark.parametrize(
    "component,version,min_version,expected",
    [
        ["Plone", "6.0", "6", ""],
        ["Plone", "6.0.10", "6", ""],
        ["Plone", "6.0.10.1", "6", ""],
        ["Plone", "6.0.10.1", "6.0.0", ""],
        ["Plone", "6.1.0a1", "6.0.0", ""],
        ["Plone", "6.1", "6.0.0", ""],
        ["Plone", "6.0.0b1", "6.0.0", "6.0.0b1 is not a valid Plone version."],
        ["Plone", "5.2.35", "6", "5.2.35 is not a valid Plone version."],
        ["Something", "foo", "6", "foo is not a valid Something version."],
        ["Volto", "18.0.0-alpha.27", "17.9", ""],
        [
            "Volto",
            "18.0.0-alpha.27",
            "18",
            "18.0.0-alpha.27 is not a valid Volto version.",
        ],
    ],
)
def test_validate_component_version(
    component: str, version: str, min_version: str, expected: str
):
    func = validators.validate_component_version
    assert func(component, version, min_version) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        (" ", "' ' is not a valid language code."),
        ("", "'' is not a valid language code."),
        ("en", ""),
        ("en-us", ""),
        ("pt-br", ""),
        ("en-", "'en-' is not a valid language code."),
        ("EN-", "'EN-' is not a valid language code."),
        ("EN-99", "'EN-99' is not a valid language code."),
    ),
)
def test_validate_language_code(value: str, expected: str):
    """Test validate_language_code function."""
    result = validators.validate_language_code(value)
    assert result == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        (" ", "' ' is not a valid Python identifier."),
        ("", "'' is not a valid Python identifier."),
        ("project title", "'project title' is not a valid Python identifier."),
        ("project_title", ""),
        ("project-title", "'project-title' is not a valid Python identifier."),
        ("projecttitle", ""),
        ("projectTitle", ""),
    ),
)
def test_validate_python_package_name(value: str, expected: str):
    """Test validate_python_package_name function."""
    result = validators.validate_python_package_name(value)
    assert result == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        (" ", "' ' is not a valid hostname."),
        ("foo.bar", ""),
        ("plone.org", ""),
        ("dev.plone.org", ""),
    ),
)
def test_validate_hostname(value: str, expected: str):
    """Test validate_hostname function."""
    result = validators.validate_hostname(value)
    assert result == expected
