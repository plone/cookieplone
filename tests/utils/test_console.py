from cookieplone._types import CookieploneTemplate
from cookieplone._types import CookieploneTemplateGroup
from cookieplone.settings import QUIET_MODE_VAR
from cookieplone.utils import console
from pathlib import Path
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from unittest.mock import patch

import pytest


@pytest.fixture
def set_console_width(monkeypatch):
    import os

    def func(width: int) -> None:
        monkeypatch.setattr(
            "os.get_terminal_size", lambda: os.terminal_size((width, 80))
        )

    return func


@pytest.fixture
def sample_templates():
    return {
        "project": CookieploneTemplate(
            name="project",
            title="A Plone Project",
            description="Create a new Plone project",
            path=Path("templates/projects/monorepo"),
        ),
        "addon": CookieploneTemplate(
            name="addon",
            title="Backend Add-on",
            description="Create a backend add-on",
            path=Path("templates/addons/backend"),
        ),
    }


@pytest.fixture
def sample_groups(sample_templates):
    return {
        "projects": CookieploneTemplateGroup(
            name="projects",
            title="Projects",
            description="Project generators",
            templates={"project": sample_templates["project"]},
        ),
        "addons": CookieploneTemplateGroup(
            name="addons",
            title="Add-ons",
            description="Add-on generators",
            templates={"addon": sample_templates["addon"]},
        ),
    }


class TestChooseBanner:
    @pytest.mark.parametrize(
        "width,banner",
        [
            (80, console.BANNER),
            (90, console.PLONE_LOGOTYPE_BANNER),
            (100, console.PLONE_LOGOTYPE_BANNER),
        ],
    )
    def test_by_terminal_width(self, set_console_width, width, banner):
        set_console_width(width)
        assert console.choose_banner() == banner

    def test_fallback_on_oserror(self, monkeypatch):
        monkeypatch.setattr(
            "os.get_terminal_size", lambda: (_ for _ in ()).throw(OSError)
        )
        assert console.choose_banner() == console.BANNER


class TestClearScreen:
    @patch("cookieplone.utils.console._console")
    def test_delegates_to_console(self, mock_console):
        console.clear_screen()
        mock_console.clear.assert_called_once()


class TestPrint:
    @patch("cookieplone.utils.console.print")
    def test_print_plone_banner(self, mock_print):
        console.print_plone_banner()
        mock_print.assert_called_once_with(console.BANNER, "bold", "blue")

    @pytest.mark.parametrize(
        "func,msg,style,color",
        [
            (console.info, "foo", "bold", "white"),
            (console.success, "foo", "bold", "green"),
            (console.error, "foo", "bold", "red"),
            (console.warning, "foo", "bold", "yellow"),
        ],
    )
    @patch("cookieplone.utils.console.print")
    def test_level_functions(self, mock_print, func, msg, style, color):
        func(msg)
        mock_print.assert_called_once_with(msg, style, color)

    @patch("cookieplone.utils.console._print")
    def test_print_with_markup(self, mock_print):
        console.print("hello", style="bold", color="red")
        mock_print.assert_called_once_with("[bold red]hello[/bold red]")

    @patch("cookieplone.utils.console._print")
    def test_print_without_markup(self, mock_print):
        console.print("hello")
        mock_print.assert_called_once_with("hello")

    @patch("cookieplone.utils.console.base_print")
    def test__print_respects_quiet_mode(self, mock_base_print, monkeypatch):
        monkeypatch.setenv(QUIET_MODE_VAR, "1")
        console._print("should not print")
        mock_base_print.assert_not_called()

    @patch("cookieplone.utils.console.base_print")
    def test__print_outputs_when_not_quiet(self, mock_base_print, monkeypatch):
        monkeypatch.delenv(QUIET_MODE_VAR, raising=False)
        console._print("visible")
        mock_base_print.assert_called_once_with("visible")


class TestPanel:
    @patch("cookieplone.utils.console._print")
    def test_panel_without_url(self, mock_print):
        console.panel(title="Test", msg="body")
        args = mock_print.call_args[0]
        assert isinstance(args[0], Panel)

    @patch("cookieplone.utils.console._print")
    def test_panel_with_url(self, mock_print):
        console.panel(title="Test", msg="body", url="https://example.com")
        args = mock_print.call_args[0]
        assert isinstance(args[0], Panel)


class TestCreateTable:
    def test_returns_table(self):
        columns = [
            {"title": "#", "style": "cyan"},
            {"title": "Name", "style": "blue"},
        ]
        rows = [("1", "Alice"), ("2", "Bob")]
        result = console.create_table(columns, rows)
        assert isinstance(result, Table)
        assert result.row_count == 2


class TestStyledList:
    def test_returns_text(self):
        items = [("Title A", "Desc A"), ("Title B", "Desc B")]
        result = console.styled_list(items)
        assert isinstance(result, Text)
        plain = result.plain
        assert "1" in plain
        assert "Title A" in plain
        assert "Desc A" in plain
        assert "2" in plain
        assert "Title B" in plain

    def test_empty_list(self):
        result = console.styled_list([])
        assert isinstance(result, Text)
        assert result.plain == "\n"


class TestListAvailableTemplates:
    def test_returns_text(self, sample_templates):
        result = console.list_available_templates(sample_templates)
        assert isinstance(result, Text)
        assert "A Plone Project" in result.plain
        assert "Backend Add-on" in result.plain


class TestListAvailableGroups:
    def test_returns_text(self, sample_groups):
        result = console.list_available_groups(sample_groups)
        assert isinstance(result, Text)
        assert "Projects" in result.plain
        assert "Add-ons" in result.plain


class TestWelcomeScreen:
    @patch("cookieplone.utils.console.base_print")
    def test_with_groups(self, mock_print, sample_groups):
        console.welcome_screen(groups=sample_groups)
        mock_print.assert_called_once()
        panel = mock_print.call_args[0][0]
        assert isinstance(panel, Panel)

    @patch("cookieplone.utils.console.base_print")
    def test_with_templates(self, mock_print, sample_templates):
        console.welcome_screen(templates=sample_templates)
        mock_print.assert_called_once()
        panel = mock_print.call_args[0][0]
        assert isinstance(panel, Panel)

    @patch("cookieplone.utils.console.base_print")
    def test_without_args(self, mock_print):
        console.welcome_screen()
        mock_print.assert_called_once()
        panel = mock_print.call_args[0][0]
        assert isinstance(panel, Panel)


class TestVersionScreen:
    @patch("cookieplone.utils.console.base_print")
    def test_calls_base_print(self, mock_print):
        console.version_screen()
        mock_print.assert_called_once()


class TestInfoScreen:
    @patch("cookieplone.utils.console.base_print")
    def test_renders_panel(self, mock_print):
        console.info_screen(repository="/var/repo", passwd="", tag="main")
        mock_print.assert_called_once()
        panel = mock_print.call_args[0][0]
        assert isinstance(panel, Panel)


class TestQuietMode:
    def test_enable_quiet_mode(self, monkeypatch):
        monkeypatch.delenv(QUIET_MODE_VAR, raising=False)
        console.enable_quiet_mode()
        import os

        assert os.environ.get(QUIET_MODE_VAR) == "1"

    def test_disable_quiet_mode(self, monkeypatch):
        monkeypatch.setenv(QUIET_MODE_VAR, "1")
        console.disable_quiet_mode()
        import os

        assert os.environ.get(QUIET_MODE_VAR) is None

    def test_context_manager(self, monkeypatch):
        import os

        monkeypatch.delenv(QUIET_MODE_VAR, raising=False)
        with console.quiet_mode():
            assert os.environ.get(QUIET_MODE_VAR) == "1"
        assert os.environ.get(QUIET_MODE_VAR) is None

    def test_context_manager_cleans_up_on_exception(self, monkeypatch):
        import os

        monkeypatch.delenv(QUIET_MODE_VAR, raising=False)
        with pytest.raises(ValueError, match="boom"), console.quiet_mode():
            assert os.environ.get(QUIET_MODE_VAR) == "1"
            raise ValueError("boom")
        assert os.environ.get(QUIET_MODE_VAR) is None
