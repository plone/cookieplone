"""Tests for cookieplone.utils.post_gen."""

from collections import OrderedDict
from cookieplone.utils.post_gen import PostGenAction
from cookieplone.utils.post_gen import create_namespace_packages
from cookieplone.utils.post_gen import initialize_git_repository
from cookieplone.utils.post_gen import move_files
from cookieplone.utils.post_gen import remove_files_by_key
from cookieplone.utils.post_gen import run_make_format
from cookieplone.utils.post_gen import run_post_gen_actions
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


@pytest.fixture
def context():
    """A minimal cookiecutter context."""
    return OrderedDict({"title": "My Project", "python_package_name": "my.addon"})


@pytest.fixture
def output_dir(tmp_path):
    """A temporary output directory."""
    project = tmp_path / "my-project"
    project.mkdir()
    return project


class TestRunPostGenActions:
    """Tests for run_post_gen_actions."""

    @patch("cookieplone.utils.post_gen.console_print")
    def test_empty_actions(self, mock_print, context, output_dir):
        """No-op when actions list is empty."""
        run_post_gen_actions(context, output_dir, [])
        mock_print.assert_not_called()

    @patch("cookieplone.utils.post_gen.console_print")
    def test_disabled_action_skipped(self, mock_print, context, output_dir):
        """Disabled actions are skipped with an Ignoring message."""
        handler = MagicMock()
        actions: list[PostGenAction] = [
            {"handler": handler, "title": "Skip me", "enabled": False},
        ]
        run_post_gen_actions(context, output_dir, actions)
        handler.assert_not_called()
        mock_print.assert_called_once_with(" -> Ignoring (Skip me)")

    @patch("cookieplone.utils.post_gen.console_print")
    def test_enabled_action_called(self, mock_print, context, output_dir):
        """Enabled actions are called with deep-copied context and output_dir."""
        handler = MagicMock()
        actions: list[PostGenAction] = [
            {"handler": handler, "title": "Do stuff", "enabled": True},
        ]
        run_post_gen_actions(context, output_dir, actions)
        handler.assert_called_once()
        call_args = handler.call_args[0]
        # Receives a deep copy, not the original
        assert call_args[0] is not context
        assert call_args[0] == context
        assert call_args[1] == output_dir
        mock_print.assert_called_once_with(" -> Do stuff")

    @patch("cookieplone.utils.post_gen.console_print")
    def test_mixed_enabled_disabled(self, mock_print, context, output_dir):
        """Mix of enabled and disabled actions."""
        h1 = MagicMock()
        h2 = MagicMock()
        h3 = MagicMock()
        actions: list[PostGenAction] = [
            {"handler": h1, "title": "First", "enabled": True},
            {"handler": h2, "title": "Second", "enabled": False},
            {"handler": h3, "title": "Third", "enabled": True},
        ]
        run_post_gen_actions(context, output_dir, actions)
        h1.assert_called_once()
        h2.assert_not_called()
        h3.assert_called_once()

    @patch("cookieplone.utils.post_gen.console_print")
    def test_int_coercible_enabled(self, mock_print, context, output_dir):
        """Enabled value is coerced via int() — '0' is falsy, '1' is truthy."""
        handler = MagicMock()
        actions: list[PostGenAction] = [
            {"handler": handler, "title": "Coerced", "enabled": "1"},
        ]
        run_post_gen_actions(context, output_dir, actions)
        handler.assert_called_once()

    @patch("cookieplone.utils.post_gen.console_print")
    def test_preserves_execution_order(self, mock_print, context, output_dir):
        """Actions execute in list order."""
        calls = []
        for i in range(3):
            h = MagicMock(side_effect=lambda *a, idx=i: calls.append(idx))
            actions = [{"handler": h, "title": f"Step {i}", "enabled": True}]
            run_post_gen_actions(context, output_dir, actions)
        assert calls == [0, 1, 2]


class TestInitializeGitRepository:
    """Tests for initialize_git_repository handler."""

    @patch("cookieplone.utils.post_gen.initialize_repository")
    def test_calls_initialize_and_adds(self, mock_init, context, output_dir):
        """Initializes repo and runs a second git add."""
        mock_repo = MagicMock()
        mock_init.return_value = mock_repo

        initialize_git_repository(context, output_dir)

        mock_init.assert_called_once_with(output_dir)
        mock_repo.git.add.assert_called_once_with(output_dir)


class TestCreateNamespacePackages:
    """Tests for create_namespace_packages handler."""

    @patch("cookieplone.utils.post_gen._create_namespace_packages")
    def test_calls_with_package_name(self, mock_create, output_dir):
        """Delegates to plone.create_namespace_packages with context values."""
        ctx = OrderedDict({"python_package_name": "plone.app.testing"})
        create_namespace_packages(ctx, output_dir)
        mock_create.assert_called_once_with(output_dir, "plone.app.testing", "native")

    @patch("cookieplone.utils.post_gen._create_namespace_packages")
    def test_respects_namespace_style(self, mock_create, output_dir):
        """Uses namespace_style from context when present."""
        ctx = OrderedDict({
            "python_package_name": "plone.app.testing",
            "namespace_style": "pkgutil",
        })
        create_namespace_packages(ctx, output_dir)
        mock_create.assert_called_once_with(output_dir, "plone.app.testing", "pkgutil")

    @patch("cookieplone.utils.post_gen._create_namespace_packages")
    def test_skips_non_namespaced(self, mock_create, output_dir):
        """Skips when package_name has no dots."""
        ctx = OrderedDict({"python_package_name": "myaddon"})
        create_namespace_packages(ctx, output_dir)
        mock_create.assert_not_called()

    @patch("cookieplone.utils.post_gen._create_namespace_packages")
    def test_skips_empty_package_name(self, mock_create, output_dir):
        """Skips when python_package_name is missing."""
        ctx = OrderedDict({})
        create_namespace_packages(ctx, output_dir)
        mock_create.assert_not_called()


class TestRemoveFilesByKey:
    """Tests for remove_files_by_key factory."""

    def test_returns_callable(self):
        """Factory returns a PostGenHandler."""
        handler = remove_files_by_key({"k": ["a.txt"]}, "k")
        assert callable(handler)

    @patch("cookieplone.utils.post_gen.remove_files")
    def test_removes_matching_files(self, mock_remove, context, output_dir):
        """Handler removes files listed under the given key."""
        to_remove = {"devops-ansible": ["devops/ansible", "devops/vars"]}
        handler = remove_files_by_key(to_remove, "devops-ansible")
        handler(context, output_dir)
        mock_remove.assert_called_once_with(
            output_dir, ["devops/ansible", "devops/vars"]
        )

    @patch("cookieplone.utils.post_gen.remove_files")
    def test_missing_key_is_noop(self, mock_remove, context, output_dir):
        """Handler is a no-op when key is not in the dict."""
        handler = remove_files_by_key({"other": ["x"]}, "missing")
        handler(context, output_dir)
        mock_remove.assert_not_called()


class TestMoveFiles:
    """Tests for move_files factory."""

    def test_returns_callable(self):
        """Factory returns a PostGenHandler."""
        handler = move_files([("a", "b")])
        assert callable(handler)

    def test_renames_files(self, context, output_dir):
        """Handler renames source to destination."""
        src = output_dir / "docs" / ".readthedocs.yaml"
        src.parent.mkdir(parents=True)
        src.write_text("config")

        handler = move_files([("docs/.readthedocs.yaml", ".readthedocs.yml")])
        handler(context, output_dir)

        assert not src.exists()
        assert (output_dir / ".readthedocs.yml").read_text() == "config"

    def test_creates_parent_dirs(self, context, output_dir):
        """Handler creates destination parent directories."""
        src = output_dir / "flat.txt"
        src.write_text("data")

        handler = move_files([("flat.txt", "deep/nested/flat.txt")])
        handler(context, output_dir)

        assert not src.exists()
        assert (output_dir / "deep" / "nested" / "flat.txt").read_text() == "data"

    def test_missing_source_skipped(self, context, output_dir):
        """Handler skips pairs where source does not exist."""
        handler = move_files([("nonexistent.txt", "dest.txt")])
        handler(context, output_dir)  # Should not raise
        assert not (output_dir / "dest.txt").exists()

    def test_multiple_pairs(self, context, output_dir):
        """Handler processes multiple pairs in order."""
        (output_dir / "a.txt").write_text("A")
        (output_dir / "b.txt").write_text("B")

        handler = move_files([("a.txt", "moved_a.txt"), ("b.txt", "moved_b.txt")])
        handler(context, output_dir)

        assert (output_dir / "moved_a.txt").read_text() == "A"
        assert (output_dir / "moved_b.txt").read_text() == "B"


class TestRunMakeFormat:
    """Tests for run_make_format factory."""

    def test_returns_callable(self):
        """Factory returns a PostGenHandler."""
        handler = run_make_format()
        assert callable(handler)

    @patch("cookieplone.utils.post_gen.subprocess.run")
    def test_runs_make_in_output_dir(self, mock_run, context, output_dir):
        """Handler runs make in output_dir when no folder specified."""
        (output_dir / "Makefile").write_text("format:\n\techo ok")
        handler = run_make_format()
        handler(context, output_dir)
        mock_run.assert_called_once_with(
            ["make", "format"],
            cwd=output_dir,
            capture_output=True,
        )

    @patch("cookieplone.utils.post_gen.subprocess.run")
    def test_runs_make_in_subfolder(self, mock_run, context, output_dir):
        """Handler runs make in the specified subfolder."""
        backend = output_dir / "backend"
        backend.mkdir()
        (backend / "Makefile").write_text("format:\n\techo ok")
        handler = run_make_format("format", "backend")
        handler(context, output_dir)
        mock_run.assert_called_once_with(
            ["make", "format"],
            cwd=backend,
            capture_output=True,
        )

    @patch("cookieplone.utils.post_gen.subprocess.run")
    def test_custom_target(self, mock_run, context, output_dir):
        """Handler respects custom make target."""
        (output_dir / "Makefile").write_text("lint:\n\techo ok")
        handler = run_make_format("lint")
        handler(context, output_dir)
        mock_run.assert_called_once_with(
            ["make", "lint"],
            cwd=output_dir,
            capture_output=True,
        )

    @patch("cookieplone.utils.post_gen.subprocess.run")
    def test_no_makefile_skips(self, mock_run, context, output_dir):
        """Handler is a no-op when Makefile is missing."""
        handler = run_make_format()
        handler(context, output_dir)
        mock_run.assert_not_called()
