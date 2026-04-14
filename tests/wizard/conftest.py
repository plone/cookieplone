"""Shared fixtures for wizard tests."""

from cookieplone.config.state import CookieploneState
from cookieplone.settings import RENDERER_VAR
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.cookiecutter import CookiecutterRenderer
from unittest.mock import MagicMock

import os
import pytest


@pytest.fixture(autouse=True, scope="session")
def _clean_renderer_env():
    """Ensure COOKIEPLONE_RENDERER is unset for all wizard tests."""
    old = os.environ.pop(RENDERER_VAR, None)
    yield
    if old is not None:
        os.environ[RENDERER_VAR] = old


@pytest.fixture()
def renderer_klass() -> type[BaseRenderer]:
    """Use the CookiecutterRenderer for wizard tests."""
    return CookiecutterRenderer


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
