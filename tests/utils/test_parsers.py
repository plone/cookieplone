import pytest

from cookieplone.utils.parsers import parse_boolean


class TestParseBoolean:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("1", True),
            ("yes", True),
            ("y", True),
            ("YES", True),
            ("Y", True),
            ("Yes", True),
            ("0", False),
            ("no", False),
            ("n", False),
            ("false", False),
            ("", False),
            ("anything", False),
        ],
    )
    def test_parse_boolean(self, value, expected):
        assert parse_boolean(value) is expected
