import pytest


@pytest.fixture(scope="session")
def validators(context) -> dict[str, str]:
    """Fixture to provide the validators defined in the context."""
    return context.get("__validators__", {})


@pytest.fixture
def context_project(read_config_file):
    """Return the parsed v1 project config dict from ``config/v1-project.json``."""
    data = read_config_file("config/v1-project.json")
    return data


@pytest.fixture
def extra_project(read_config_file):
    """Return the parsed extra-context dict from ``config/extra-v1-project.json``."""
    data = read_config_file("config/extra-v1-project.json")
    return data


@pytest.fixture
def replay_project(read_config_file):
    """Return the parsed replay config dict from ``config/replay-v1-project.json``.

    This fixture intentionally omits three keys present in the full project
    config so that tests can verify behaviour when keys are missing from a
    replay file.
    """
    data = read_config_file("config/replay-v1-project.json")
    return data


@pytest.fixture
def work_dir(base_template_path, monkeypatch):
    """Create a temporary template directory and set it as the working directory.

    Changes the process working directory to a fresh temporary path for the
    duration of the test, then restores it automatically via ``monkeypatch``.

    :returns: The :class:`~pathlib.Path` of the temporary working directory.
    """
    cwd = base_template_path()
    monkeypatch.chdir(cwd)
    return cwd
