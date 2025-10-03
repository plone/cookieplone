from unittest.mock import patch

import pytest

from cookieplone.utils import console


@pytest.fixture
def set_console_width(monkeypatch):
    import os

    def func(width: int) -> None:
        monkeypatch.setattr(
            "os.get_terminal_size", lambda: os.terminal_size((width, 80))
        )

    return func


@patch("cookieplone.utils.console.print")
def test_print_plone_banner(mock_print):
    console.print_plone_banner()
    mock_print.assert_called_once_with(console.BANNER, "bold", "blue")


@pytest.mark.parametrize(
    "width,banner",
    [
        (80, console.BANNER),
        (90, console.PLONE_LOGOTYPE_BANNER),
        (100, console.PLONE_LOGOTYPE_BANNER),
    ],
)
def test_choose_banner(set_console_width, width: int, banner: str):
    set_console_width(width)
    assert console.choose_banner() == banner


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
