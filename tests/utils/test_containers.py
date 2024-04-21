import pytest

from cookieplone.utils import containers


@pytest.mark.parametrize(
    "registry,expected",
    [
        ["docker_hub", ""],
        ["github", "ghcr.io/"],
        ["gitlab", "registry.gitlab.com/"],
        ["bitbucket", ""],
    ],
)
def test_image_prefix(registry, expected):
    assert containers.image_prefix(registry) == expected
