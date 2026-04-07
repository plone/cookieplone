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

    @pytest.mark.parametrize(
        "value,expected",
        [
            (True, True),
            (False, False),
            (1, True),
            (0, False),
            (2, True),
        ],
        ids=["bool-true", "bool-false", "int-1", "int-0", "int-2"],
    )
    def test_parse_boolean_accepts_bool_and_int(self, value, expected):
        """parse_boolean handles bool and int inputs, not just str."""
        assert parse_boolean(value) is expected
