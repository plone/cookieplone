import json

import pytest

from cookieplone.config.state import Answers
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


class TestWriteAnswers:
    """Tests for write_answers."""

    @pytest.fixture
    def wizard_answers(self):
        return Answers(
            answers={"_folder_name": "my-project", "title": "My Project"},
            user_answers={"title": "My Project", "language": "en"},
            initial_answers={"title": "Initial Project", "language": "pt-br"},
        )

    def test_writes_template_key_in_interactive_mode(
        self, wizard_answers, tmp_path, monkeypatch
    ):
        """__template__ is persisted in the JSON file for interactive runs."""
        monkeypatch.chdir(tmp_path)
        path = answers.write_answers(wizard_answers, "project", no_input=False)
        data = json.loads(path.read_text())
        assert data["__template__"] == "project"

    def test_writes_template_key_in_no_input_mode(
        self, wizard_answers, tmp_path, monkeypatch
    ):
        """__template__ is persisted in the JSON file when --no-input is used."""
        monkeypatch.chdir(tmp_path)
        path = answers.write_answers(wizard_answers, "project", no_input=True)
        data = json.loads(path.read_text())
        assert data["__template__"] == "project"

    def test_persists_user_answers_in_interactive_mode(
        self, wizard_answers, tmp_path, monkeypatch
    ):
        """Interactive runs write user_answers, not initial_answers."""
        monkeypatch.chdir(tmp_path)
        path = answers.write_answers(wizard_answers, "project", no_input=False)
        data = json.loads(path.read_text())
        assert data["title"] == "My Project"
        assert data["language"] == "en"

    def test_persists_initial_answers_in_no_input_mode(
        self, wizard_answers, tmp_path, monkeypatch
    ):
        """Non-interactive runs write initial_answers, not user_answers."""
        monkeypatch.chdir(tmp_path)
        path = answers.write_answers(wizard_answers, "project", no_input=True)
        data = json.loads(path.read_text())
        assert data["title"] == "Initial Project"
        assert data["language"] == "pt-br"

    def test_does_not_mutate_user_answers(self, wizard_answers, tmp_path, monkeypatch):
        """write_answers must not mutate the live wizard state."""
        monkeypatch.chdir(tmp_path)
        original_user = dict(wizard_answers.user_answers)
        original_initial = dict(wizard_answers.initial_answers)
        answers.write_answers(wizard_answers, "project", no_input=False)
        assert wizard_answers.user_answers == original_user
        assert "__template__" not in wizard_answers.user_answers
        answers.write_answers(wizard_answers, "project", no_input=True)
        assert wizard_answers.initial_answers == original_initial
        assert "__template__" not in wizard_answers.initial_answers

    def test_uses_folder_name_in_filename(self, wizard_answers, tmp_path, monkeypatch):
        """Filename uses _folder_name from answers when present."""
        monkeypatch.chdir(tmp_path)
        path = answers.write_answers(wizard_answers, "project", no_input=False)
        assert path.name == ".cookieplone_answers_my-project.json"

    def test_falls_back_to_template_name_in_filename(self, tmp_path, monkeypatch):
        """Filename falls back to template_name when _folder_name is missing."""
        monkeypatch.chdir(tmp_path)
        wizard = Answers(
            answers={},
            user_answers={"title": "Test"},
            initial_answers={"title": "Test"},
        )
        path = answers.write_answers(wizard, "fallback-template", no_input=False)
        assert path.name == ".cookieplone_answers_fallback-template.json"
