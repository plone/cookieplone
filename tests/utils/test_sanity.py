from typing import Any

import pytest

from cookieplone import data
from cookieplone.utils import sanity


def check_instance(value: Any, type_: type) -> str:
    """Check if value is instance of type_."""
    check = isinstance(value, type_)
    return "" if check else f"Value is not a {type_}"


@pytest.fixture
def valid_checks():
    return [
        data.SanityCheck("IsString", check_instance, ["", str], "error"),
        data.SanityCheck("IsDict", check_instance, [{}, dict], "error"),
        data.SanityCheck("IsFloat", check_instance, [1, float], "warning"),
    ]


def test_run_sanity_checks_pass(valid_checks):
    func = sanity.run_sanity_checks
    result = func(checks=valid_checks)
    assert result.status
    assert result.message == "Ran 3 checks and they passed."


@pytest.fixture
def invalid_checks():
    return [
        data.SanityCheck("IsString", check_instance, ["", str], "error"),
        data.SanityCheck("IsDict", check_instance, [{}, dict], "error"),
        data.SanityCheck("IsFloat", check_instance, [1, float], "error"),
    ]


def test_run_sanity_checks_fail(invalid_checks):
    func = sanity.run_sanity_checks
    result = func(checks=invalid_checks)
    assert result.status is False
    assert result.message == "Ran 3 checks and they failed."
