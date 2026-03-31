"""Tests for PLONE_PYTHON mapping."""

import pytest

from cookieplone import settings


def test_plone_60_exists():
    """Plone 6.0 has Python version support defined."""
    assert "6.0" in settings.PLONE_PYTHON


def test_plone_61_exists():
    """Plone 6.1 has Python version support defined."""
    assert "6.1" in settings.PLONE_PYTHON


@pytest.mark.parametrize("version", ["6.0", "6.1"])
def test_entries_are_python_version_support(version: str):
    """Each entry is a PythonVersionSupport instance."""
    assert isinstance(settings.PLONE_PYTHON[version], settings.PythonVersionSupport)


@pytest.mark.parametrize("version", ["6.0", "6.1"])
def test_earliest_in_supported(version: str):
    """Earliest version is in the supported list."""
    pvs = settings.PLONE_PYTHON[version]
    assert pvs.earliest in pvs.supported


@pytest.mark.parametrize("version", ["6.0", "6.1"])
def test_latest_in_supported(version: str):
    """Latest version is in the supported list."""
    pvs = settings.PLONE_PYTHON[version]
    assert pvs.latest in pvs.supported


@pytest.mark.parametrize("version", ["6.0", "6.1"])
def test_earliest_before_latest(version: str):
    """Earliest version appears before latest in the supported list."""
    pvs = settings.PLONE_PYTHON[version]
    assert pvs.supported.index(pvs.earliest) <= pvs.supported.index(pvs.latest)
