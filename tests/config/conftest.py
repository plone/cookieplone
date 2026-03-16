import pytest


@pytest.fixture(scope="session")
def validators(context) -> dict[str, str]:
    """Fixture to provide the validators defined in the context."""
    return context.get("__validators__", {})


@pytest.fixture
def context_project(read_config_file):
    data = read_config_file("config/v1-project.json")
    return data


@pytest.fixture
def extra_project(read_config_file):
    data = read_config_file("config/extra-v1-project.json")
    return data


@pytest.fixture
def replay_project(read_config_file):
    # Removed 3 keys
    data = read_config_file("config/replay-v1-project.json")
    return data
