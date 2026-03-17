from typing import Any

import pytest

from cookieplone import validators


@pytest.mark.parametrize(
    "value,expected",
    (
        ("", False),
        (" ", True),
        ("a", True),
        ("1234", True),
        ("volto", True),
    ),
)
def test_not_empty(value: Any, expected: bool):
    return validators.not_empty(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("pt", True),
        ("pt-br", True),
        ("en", True),
        (" ", False),
    ),
)
def test_language_code(value: Any, expected: bool):
    return validators.language_code(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("Plone", True),
        (" Plone", False),
        ("Plone ", False),
        ("Products.CMFPlone", True),
        ("@plone/components", True),
    ),
)
def test_python_package_name(value: Any, expected: bool):
    return validators.python_package_name(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("foo.com", True),
        ("hostname.com", True),
        (" hostname.com ", False),
    ),
)
def test_hostname(value: Any, expected: bool):
    return validators.hostname(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("@plone/components", True),
        ("volto-addon", True),
        ("plone.api", False),
    ),
)
def test_volto_addon_name(value: Any, expected: bool):
    return validators.volto_addon_name(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("@plone/components", True),
        ("volto-addon", True),
        ("plone.api", False),
    ),
)
def test_npm_package_name(value: Any, expected: bool):
    return validators.npm_package_name(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("6.1.4", True),
        ("6.1.0", True),
        (" ", False),
        ("Seven", False),
    ),
)
def test_plone_version(value: Any, expected: bool):
    return validators.plone_version(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("19.0.0", True),
        ("18.12.3", True),
        (" ", False),
        ("Seven", False),
    ),
)
def test_volto_version(value: Any, expected: bool):
    return validators.volto_version(value) == expected
