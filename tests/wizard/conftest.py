"""Shared fixtures for wizard tests."""

from unittest.mock import MagicMock

import pytest

from cookieplone.config.state import CookieploneState


@pytest.fixture()
def minimal_schema():
    """A minimal v2 schema."""
    return {
        "version": "2.0",
        "properties": {
            "title": {
                "type": "string",
                "default": "My Project",
            }
        },
    }


@pytest.fixture()
def state(minimal_schema):
    """A CookieploneState with a minimal schema."""
    return CookieploneState(
        schema=minimal_schema,
        data={"cookiecutter": {"title": "My Project"}},
        root_key="cookiecutter",
        extensions=[],
    )


@pytest.fixture()
def mock_get_renderer(monkeypatch):
    """Patch cookieplone.wizard.get_renderer."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.wizard.get_renderer", mock)
    return mock


@pytest.fixture()
def mock_create_form(monkeypatch):
    """Patch cookieplone.wizard.create_form."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.wizard.create_form", mock)
    return mock
