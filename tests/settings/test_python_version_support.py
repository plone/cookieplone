"""Tests for PythonVersionSupport dataclass."""

from cookieplone import settings


def test_attributes():
    """PythonVersionSupport has expected attributes."""
    pvs = settings.PythonVersionSupport(
        supported=["3.12", "3.13"],
        earliest="3.12",
        latest="3.13",
    )
    assert pvs.supported == ["3.12", "3.13"]
    assert pvs.earliest == "3.12"
    assert pvs.latest == "3.13"
