import pytest
from click.exceptions import BadParameter

from cookieplone import cli


@pytest.mark.parametrize(
    "value,config_data,expected",
    [
        ([], {}, {}),
        (["foo=bar", "bar=bar"], {}, {"foo": "bar", "bar": "bar"}),
        (["foo=1", "bar=2"], {}, {"foo": "1", "bar": "2"}),
        (["foo=1", "bar=2"], {"foobar": "1"}, {"foo": "1", "bar": "2", "foobar": "1"}),
    ],
)
def test_parse_extra_context(
    value: list[str], config_data: dict[str, str], expected: dict
):
    func = cli.parse_extra_context
    assert func(value, config_data) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, []),
        ([], []),
        (["foo=bar", "bar=bar"], ["foo=bar", "bar=bar"]),
        (["foo=1", "bar=2"], ["foo=1", "bar=2"]),
    ],
)
def test_validate_extra_context_pass(value: list[str] | None, expected: list):
    func = cli.validate_extra_context
    assert func(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (["foo=bar", "bar2"], "bar2"),
        (["foo-1", "bar=2"], "foo-1"),
    ],
)
def test_validate_extra_context_fail(value: list[str] | None, expected: str):
    func = cli.validate_extra_context
    with pytest.raises(BadParameter) as exc:
        func(value)
    assert expected in str(exc)
