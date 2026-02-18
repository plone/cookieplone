import pytest

from cookieplone.wizard import parser


@pytest.mark.parametrize(
    "key,name",
    [
        ("title", "not_empty"),
        ("description", "not_empty"),
        ("plone_version", "plone_version"),
        ("volto_version", "volto_version"),
    ],
)
def test__get_validator(validators, key: str, name: str):
    """Test that the correct validator is returned for a given key."""
    validator = parser._get_validator(validators, key)
    assert validator is not None
    assert callable(validator)
    assert validator.__name__ == name
