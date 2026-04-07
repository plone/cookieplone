"""Tests for cookieplone.exceptions."""

from cookieplone.exceptions import CookieploneException
from cookieplone.exceptions import GeneratorException
from cookieplone.exceptions import OutputDirExistsException
from cookieplone.exceptions import PreFlightException
from unittest.mock import MagicMock

import pytest


class TestCookieploneException:
    """Tests for CookieploneException."""

    def test_str_returns_message(self):
        exc = CookieploneException("something went wrong")
        assert str(exc) == "something went wrong"

    def test_message_attribute(self):
        exc = CookieploneException("something went wrong")
        assert exc.message == "something went wrong"


class TestPreFlightException:
    """Tests for PreFlightException."""

    def test_str_returns_message(self):
        exc = PreFlightException("hook failed")
        assert str(exc) == "hook failed"

    def test_message_attribute(self):
        exc = PreFlightException("hook failed")
        assert exc.message == "hook failed"

    def test_is_cookieplone_exception(self):
        exc = PreFlightException("hook failed")
        assert isinstance(exc, CookieploneException)


class TestGeneratorException:
    """Tests for GeneratorException."""

    @pytest.fixture
    def mock_state(self):
        return MagicMock()

    def test_str_returns_message(self, mock_state):
        exc = GeneratorException("generation failed", state=mock_state)
        assert str(exc) == "generation failed"

    def test_message_attribute(self, mock_state):
        exc = GeneratorException("generation failed", state=mock_state)
        assert exc.message == "generation failed"

    def test_original_exception_preserved(self, mock_state):
        original = ValueError("root cause")
        exc = GeneratorException("wrapped", state=mock_state, original=original)
        assert exc.original is original

    def test_state_preserved(self, mock_state):
        exc = GeneratorException("failed", state=mock_state)
        assert exc.state is mock_state

    def test_is_cookieplone_exception(self, mock_state):
        exc = GeneratorException("failed", state=mock_state)
        assert isinstance(exc, CookieploneException)

    def test_str_not_empty_when_wrapping_output_dir_error(self, mock_state):
        """Regression test for #140: str() must not return empty string."""
        original = Exception("Directory already exists")
        exc = GeneratorException(
            message=str(original), state=mock_state, original=original
        )
        assert str(exc) == "Directory already exists"
        assert exc.message == "Directory already exists"


class TestOutputDirExistsException:
    """Tests for OutputDirExistsException."""

    @pytest.fixture
    def mock_state(self):
        return MagicMock()

    def test_str_contains_directory_path(self, mock_state):
        exc = OutputDirExistsException(
            message="/home/user/my-project", state=mock_state
        )
        assert "/home/user/my-project" in str(exc)
        assert "already exists" in str(exc)
        assert "--overwrite-if-exists" in str(exc)

    def test_message_attribute(self, mock_state):
        exc = OutputDirExistsException(
            message="/home/user/my-project", state=mock_state
        )
        assert "/home/user/my-project" in exc.message
        assert "already exists" in exc.message

    def test_original_exception_preserved(self, mock_state):
        original = Exception("dir exists")
        exc = OutputDirExistsException(
            message="/home/user/my-project", state=mock_state, original=original
        )
        assert exc.original is original

    def test_state_preserved(self, mock_state):
        exc = OutputDirExistsException(
            message="/home/user/my-project", state=mock_state
        )
        assert exc.state is mock_state

    def test_is_generator_exception(self, mock_state):
        exc = OutputDirExistsException(
            message="/home/user/my-project", state=mock_state
        )
        assert isinstance(exc, GeneratorException)

    def test_is_cookieplone_exception(self, mock_state):
        exc = OutputDirExistsException(
            message="/home/user/my-project", state=mock_state
        )
        assert isinstance(exc, CookieploneException)

    def test_empty_path_fallback(self, mock_state):
        """When path cannot be determined, message still makes sense."""
        exc = OutputDirExistsException(message="", state=mock_state)
        assert "already exists" in str(exc)
        assert "--overwrite-if-exists" in str(exc)
