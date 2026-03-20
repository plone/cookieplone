import pytest

from cookieplone.utils import answers


@pytest.mark.parametrize(
    "raw_answers,expected_keys",
    (
        (
            {
                "key1": "value",
                "key2": "value",
                "__key": "value",
                "__key2": "value",
                "__generator_sha": "1234",
                "__cookieplone_repository_path": "/path",
            },
            {"key1", "key2", "__generator_sha", "__cookieplone_repository_path"},
        ),
        (
            {
                "__key": "value",
                "__key2": "value",
                "__cookieplone_template": "template",
                "__generator_signature": "Foo",
            },
            {
                "__cookieplone_template",
                "__generator_signature",
            },
        ),
    ),
)
def test_remove_internal_keys(raw_answers: dict, expected_keys: set[str]):
    func = answers.remove_internal_keys
    result = set(func(raw_answers))
    assert len(expected_keys - result) == 0
