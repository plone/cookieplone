"""Tests for settings module-level constants."""

from cookieplone import settings


def test_plone_min_version():
    """PLONE_MIN_VERSION is set."""
    assert settings.PLONE_MIN_VERSION


def test_default_config_has_required_keys():
    """DEFAULT_CONFIG has the expected keys."""
    expected_keys = {
        "cookiecutters_dir",
        "replay_dir",
        "default_context",
        "abbreviations",
    }
    assert set(settings.DEFAULT_CONFIG.keys()) == expected_keys


def test_builtin_abbreviations():
    """BUILTIN_ABBREVIATIONS has gh, gl, bb."""
    assert "gh" in settings.BUILTIN_ABBREVIATIONS
    assert "gl" in settings.BUILTIN_ABBREVIATIONS
    assert "bb" in settings.BUILTIN_ABBREVIATIONS


def test_default_config_abbreviations_match():
    """DEFAULT_CONFIG abbreviations point to BUILTIN_ABBREVIATIONS."""
    assert settings.DEFAULT_CONFIG["abbreviations"] is settings.BUILTIN_ABBREVIATIONS


def test_repo_default():
    """REPO_DEFAULT is set."""
    assert settings.REPO_DEFAULT


def test_default_validators_keys():
    """DEFAULT_VALIDATORS has expected validator keys."""
    expected = {
        "plone_version",
        "volto_version",
        "python_package_name",
        "hostname",
        "language_code",
    }
    assert set(settings.DEFAULT_VALIDATORS.keys()) == expected


def test_default_extensions_not_empty():
    """DEFAULT_EXTENSIONS contains at least one extension."""
    assert len(settings.DEFAULT_EXTENSIONS) > 0


def test_default_data_key():
    """DEFAULT_DATA_KEY is 'cookiecutter'."""
    assert settings.DEFAULT_DATA_KEY == "cookiecutter"


def test_cookieplone_answers_file():
    """COOKIEPLONE_ANSWERS_FILE is set."""
    assert settings.COOKIEPLONE_ANSWERS_FILE == ".cookieplone.json"


def test_supported_python_versions():
    """SUPPORTED_PYTHON_VERSIONS is a non-empty list."""
    assert isinstance(settings.SUPPORTED_PYTHON_VERSIONS, list)
    assert len(settings.SUPPORTED_PYTHON_VERSIONS) > 0


def test_supported_node_versions():
    """SUPPORTED_NODE_VERSIONS is a non-empty list."""
    assert isinstance(settings.SUPPORTED_NODE_VERSIONS, list)
    assert len(settings.SUPPORTED_NODE_VERSIONS) > 0


def test_config_computed_keys():
    """CONFIG_COMPUTED_KEYS is a list of strings starting with __."""
    for key in settings.CONFIG_COMPUTED_KEYS:
        assert key.startswith("__")
