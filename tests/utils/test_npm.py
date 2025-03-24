import pytest

from cookieplone.utils import npm


@pytest.mark.parametrize(
    "name,expected",
    [
        ("volto-addon", False),
        ("@plone-collective/volto-addon", True),
        ("@plone/volto", True),
    ],
)
def test__is_scoped_package(name: str, expected: bool):
    func = npm._is_scoped_package
    assert func(name) is expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("volto-addon", ("", "volto-addon")),
        ("@plone-collective/volto-addon", ("@plone-collective", "volto-addon")),
        ("@plone/volto", ("@plone", "volto")),
    ],
)
def test_parse_package_name(name: str, expected: tuple[str, str]):
    func = npm.parse_package_name
    assert func(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("volto-addon", "volto-addon"),
        ("@plone-collective/volto-addon", "volto-addon"),
        ("@plone/volto", "volto"),
    ],
)
def test_unscoped_package_name(name: str, expected: str):
    func = npm.unscoped_package_name
    assert func(name) == expected
