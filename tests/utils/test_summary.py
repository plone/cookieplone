"""Tests for :mod:`cookieplone.utils.summary`."""

from cookieplone import _types as t
from cookieplone.config import Answers
from cookieplone.config import CookieploneState
from cookieplone.utils import summary
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _state(*, summary_cfg: dict | None = None, answers: Answers | None = None):
    """Build a minimal :class:`CookieploneState` for summary tests."""
    return CookieploneState(
        schema={},
        data={},
        summary=summary_cfg or {},
        answers=answers if answers is not None else Answers(),
    )


@pytest.fixture
def mock_screen(monkeypatch) -> MagicMock:
    """Patch ``console.summary_screen`` as referenced by the summary module."""
    mock = MagicMock()
    monkeypatch.setattr("cookieplone.utils.summary.console.summary_screen", mock)
    return mock


class TestSummaryInfo:
    """Tests for :func:`cookieplone.utils.summary.summary_info`."""

    def test_none_state_returns_disabled_default(self):
        """A missing state yields the disabled default summary."""
        info = summary.summary_info(None)
        assert info == t.SummaryInfo()
        assert info.enabled is False

    def test_empty_state_summary_returns_default(self):
        """A state with no summary config yields the defaults."""
        assert summary.summary_info(_state(summary_cfg={})) == t.SummaryInfo()

    def test_reads_values_from_state(self):
        """A populated ``state.summary`` is converted into a SummaryInfo."""
        state = _state(
            summary_cfg={
                "enabled": True,
                "message": "M",
                "thanks": "T",
                "signature": {"text": "X", "url": "https://x.example"},
            }
        )
        assert summary.summary_info(state) == t.SummaryInfo(
            enabled=True,
            message="M",
            thanks="T",
            signature=t.SignatureInfo(text="X", url="https://x.example"),
        )

    @pytest.mark.parametrize("enabled", [True, False])
    def test_enabled_flag_round_trips(self, enabled):
        """The ``enabled`` flag is read straight from the state summary."""
        info = summary.summary_info(_state(summary_cfg={"enabled": enabled}))
        assert info.enabled is enabled


class TestDisplaySummaryScreen:
    """Tests for :func:`cookieplone.utils.summary.display_summary_screen`."""

    def test_disabled_skips_render(self, mock_screen):
        """When the summary is disabled nothing is rendered."""
        summary.display_summary_screen(
            Path("/out"), "Volto Project", _state(summary_cfg={"enabled": False})
        )
        mock_screen.assert_not_called()

    def test_none_state_skips_render(self, mock_screen):
        """A missing state resolves to disabled and renders nothing."""
        summary.display_summary_screen(Path("/out"), "Volto Project", None)
        mock_screen.assert_not_called()

    def test_enabled_renders_with_answer_title(self, mock_screen):
        """An enabled summary uses the ``title`` answer as the screen title."""
        state = _state(
            summary_cfg={"enabled": True},
            answers=Answers(answers={"title": "My Site"}),
        )
        summary.display_summary_screen(Path("/out"), "Volto Project", state)
        mock_screen.assert_called_once()
        kwargs = mock_screen.call_args.kwargs
        assert kwargs["title"] == "My Site"
        assert kwargs["template_title"] == "Volto Project"
        assert kwargs["path"] == Path("/out")
        assert kwargs["info"].enabled is True

    def test_default_title_without_title_answer(self, mock_screen):
        """Without a ``title`` answer the default screen title is used."""
        state = _state(summary_cfg={"enabled": True}, answers=Answers(answers={}))
        summary.display_summary_screen(Path("/out"), "Volto Project", state)
        assert mock_screen.call_args.kwargs["title"] == "Generation successful"

    def test_default_title_without_answers(self, mock_screen):
        """When ``state.answers`` is missing the default title is used."""
        state = _state(summary_cfg={"enabled": True})
        state.answers = None  # type: ignore[assignment]
        summary.display_summary_screen(Path("/out"), "Volto Project", state)
        assert mock_screen.call_args.kwargs["title"] == "Generation successful"
