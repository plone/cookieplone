from typing import Any

import pytest
from tui_forms.form.question import ValidationError

from cookieplone import validators


@pytest.mark.parametrize(
    "value,valid",
    (
        ("", False),
        (" ", False),
        ("a", True),
        ("1234", True),
        ("volto", True),
    ),
)
def test_not_empty(value: Any, valid: bool):
    if valid:
        assert validators.not_empty(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.not_empty(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("pt", True),
        ("pt-br", True),
        ("en", True),
        (" ", False),
    ),
)
def test_language_code(value: Any, valid: bool):
    if valid:
        assert validators.language_code(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.language_code(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("Plone", True),
        (" Plone", False),
        ("Plone ", False),
        ("Products.CMFPlone", True),
        ("@plone/components", False),
    ),
)
def test_python_package_name(value: Any, valid: bool):
    if valid:
        assert validators.python_package_name(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.python_package_name(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("foo.com", True),
        ("hostname.com", True),
        ("", False),
        ("  ", False),
    ),
)
def test_hostname(value: Any, valid: bool):
    if valid:
        assert validators.hostname(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.hostname(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("volto-addon", True),
        ("plone.api", True),
        ("INVALID NAME", False),
    ),
)
def test_volto_addon_name(value: Any, valid: bool):
    if valid:
        assert validators.volto_addon_name(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.volto_addon_name(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("@plone/components", True),
        ("volto-addon", True),
        ("INVALID NAME", False),
    ),
)
def test_npm_package_name(value: Any, valid: bool):
    if valid:
        assert validators.npm_package_name(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.npm_package_name(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("6.1.4", True),
        ("6.1.0", True),
        (" ", False),
        ("Seven", False),
    ),
)
def test_plone_version(value: Any, valid: bool):
    if valid:
        assert validators.plone_version(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.plone_version(value)


@pytest.mark.parametrize(
    "value,valid",
    (
        ("19.0.0", True),
        ("18.12.3", True),
        (" ", False),
        ("Seven", False),
    ),
)
def test_volto_version(value: Any, valid: bool):
    if valid:
        assert validators.volto_version(value) is True
    else:
        with pytest.raises(ValidationError):
            validators.volto_version(value)


class TestValidationErrorMessages:
    """Test that validators raise ValidationError with meaningful messages."""

    def test_not_empty_message(self):
        with pytest.raises(ValidationError, match="should be provided"):
            validators.not_empty("")

    def test_language_code_message(self):
        with pytest.raises(ValidationError, match="not a valid language code"):
            validators.language_code("xyz-abc-123")

    def test_python_package_name_message(self):
        with pytest.raises(ValidationError, match="not a valid Python identifier"):
            validators.python_package_name(" Plone")

    def test_hostname_message(self):
        with pytest.raises(ValidationError, match="not a valid hostname"):
            validators.hostname("")

    def test_volto_addon_name_message(self):
        with pytest.raises(ValidationError, match="not a valid name"):
            validators.volto_addon_name("INVALID NAME")

    def test_npm_package_name_message(self):
        with pytest.raises(ValidationError, match="not a valid package name"):
            validators.npm_package_name("INVALID NAME")

    def test_plone_version_message(self):
        with pytest.raises(ValidationError, match="not a valid Plone version"):
            validators.plone_version("Seven")

    def test_volto_version_message(self):
        with pytest.raises(ValidationError, match="not supported"):
            validators.volto_version("Seven")
