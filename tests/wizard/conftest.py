import pytest


@pytest.fixture(scope="session")
def validators(context) -> dict[str, str]:
    """Fixture to provide the validators defined in the context."""
    return context.get("__validators__", {})
