import pytest

from cookieplone.utils import validators


@pytest.mark.parametrize(
    "key,value,expected",
    [
        ["foo", "", "foo should be provided"],
        ["", "", " should be provided"],
        ["foo", "not empty", ""],
        ["foo", 0, ""],
        ["foo", 0.0, ""],
        ["foo", [0], ""],
        ["foo", [], "foo should be provided"],
    ],
)
def test_validate_not_empty(key: str, value: str, expected: str):
    func = validators.validate_not_empty
    assert func(value, key) == expected


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
        ("project.title", ""),
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


@pytest.mark.parametrize(
    "value,expected",
    (
        ("volto-addon", ""),
        ("@plone/volto", "'@plone/volto' is not a valid name."),
        ("123 ", "'123 ' is not a valid name."),
        ("", "'' is not a valid name."),
    ),
)
def test_validate_volto_addon_name(value: str, expected: str):
    """Test validate_volto_addon_name function."""
    result = validators.validate_volto_addon_name(value)
    assert result == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("volto-addon", ""),
        ("@plone/volto", ""),
        ("123 ", "'123 ' is not a valid package name."),
        ("", "'' is not a valid package name."),
    ),
)
def test_validate_npm_package_name(value: str, expected: str):
    """Test validate_volto_addon_name function."""
    result = validators.validate_npm_package_name(value)
    assert result == expected


@pytest.fixture
def context():
    return {
        "__foo": "",
        "addon_name": "volto-code-block",
        "npm_package_name": "@plonegovbr/volto-code-block",
        "another": "",
    }


@pytest.fixture
def my_validators():
    from cookieplone import data
    from cookieplone.utils import validators

    return [
        data.ItemValidator("addon_name", validators.validate_volto_addon_name),
        data.ItemValidator("npm_package_name", validators.validate_npm_package_name),
        data.ItemValidator("another", validators.validate_plone_version, "warning"),
    ]


@pytest.mark.parametrize(
    "allow_empty,expected",
    (
        (True, True),
        (False, False),
    ),
)
def test_run_context_validations(
    context, my_validators, allow_empty: bool, expected: bool
):
    """Test run_context_validations function."""
    result = validators.run_context_validations(context, my_validators, allow_empty)
    assert result.status is expected


@pytest.mark.parametrize(
    "version,expected",
    (
        ("5.2.99", "5.2.99 is not a valid Plone version."),
        ("6.0.1", ""),
        ("6.1.0a3", ""),
        ("7.0.0", ""),
    ),
)
def test_validate_plone_version(version: str, expected: str):
    func = validators.validate_plone_version
    assert func(version) == expected


@pytest.mark.parametrize(
    "version,expected",
    (
        ("18.0.0-alpha.21", ""),
        ("17.0.0", "Volto version 17.0.0 is not supported by this template."),
        ("16.15.1", "Volto version 16.15.1 is not supported by this template."),
    ),
)
def test_validate_volto_version(version: str, expected: str):
    func = validators.validate_volto_version
    assert func(version) == expected
