from unittest.mock import patch

import pytest

from cookieplone.utils import console


@patch("cookieplone.utils.console.print")
def test_print_plone_banner(mock_print):
    console.print_plone_banner()
    mock_print.assert_called_once_with(console.BANNER, "bold", "blue")


@pytest.mark.parametrize(
    "func,msg,style,color",
    [
        [console.info, "foo", "bold", "white"],
        [console.success, "foo", "bold", "green"],
        [console.error, "foo", "bold", "red"],
        [console.warning, "foo", "bold", "yellow"],
    ],
)
@patch("cookieplone.utils.console.print")
def test_prints(mock_print, func, msg, style, color):
    func(msg)
    mock_print.assert_called_once_with(msg, style, color)
