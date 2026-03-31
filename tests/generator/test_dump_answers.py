"""Tests for _dump_answers."""

from unittest.mock import MagicMock

from cookieplone.config.state import Answers
from cookieplone.generator import _dump_answers


def test_calls_write_answers(mock_write_answers, tmp_path):
    """_dump_answers delegates to answers.write_answers."""
    mock_answers = MagicMock(spec=Answers)
    answers_path = tmp_path / "answers.json"
    mock_write_answers.return_value = answers_path
    result = _dump_answers(mock_answers, "project", no_input=False)
    mock_write_answers.assert_called_once_with(mock_answers, "project", False)
    assert result == answers_path


def test_passes_no_input(mock_write_answers, tmp_path):
    """_dump_answers forwards no_input parameter."""
    mock_answers = MagicMock(spec=Answers)
    mock_write_answers.return_value = tmp_path / "answers.json"
    _dump_answers(mock_answers, "project", no_input=True)
    mock_write_answers.assert_called_once_with(mock_answers, "project", True)
