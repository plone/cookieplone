"""Tests for the template-file overlay helpers in cookieplone.repository."""

from __future__ import annotations

from cookieplone import repository as r
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestOverlayCopy:
    def test_copies_all_files(self, tmp_path: Path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        dst.mkdir()
        _write(src / "a.txt", "a")
        _write(src / "sub" / "b.txt", "b")

        r._overlay_copy(src, dst)

        assert (dst / "a.txt").read_text() == "a"
        assert (dst / "sub" / "b.txt").read_text() == "b"

    def test_overwrites_existing_files(self, tmp_path: Path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        _write(src / "a.txt", "from src")
        _write(dst / "a.txt", "from dst")

        r._overlay_copy(src, dst)

        assert (dst / "a.txt").read_text() == "from src"

    def test_preserves_unaffected_dst_files(self, tmp_path: Path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        _write(src / "new.txt", "new")
        _write(dst / "kept.txt", "kept")

        r._overlay_copy(src, dst)

        assert (dst / "new.txt").read_text() == "new"
        assert (dst / "kept.txt").read_text() == "kept"


class TestBuildTemplateOverlay:
    def test_layers_combined_downstream_wins_per_file(self, tmp_path: Path):
        # Upstream template directory
        upstream_template = tmp_path / "upstream" / "templates" / "project"
        _write(upstream_template / "cookieplone.json", '{"upstream": true}')
        _write(
            upstream_template / "{{ cookiecutter.__folder_name }}" / "README.md",
            "upstream README",
        )
        _write(
            upstream_template / "{{ cookiecutter.__folder_name }}" / "other.txt",
            "untouched",
        )

        # Downstream template directory (only overrides README)
        downstream_template = tmp_path / "downstream" / "templates" / "project"
        _write(
            downstream_template / "{{ cookiecutter.__folder_name }}" / "README.md",
            "downstream README",
        )

        overlay = r._build_template_overlay(
            downstream_template,
            underlay=[(tmp_path / "upstream", "templates/project")],
        )

        # cookieplone.json comes from upstream (downstream didn't supply one)
        assert (overlay / "cookieplone.json").read_text() == '{"upstream": true}'
        # README is the downstream version
        assert (
            overlay / "{{ cookiecutter.__folder_name }}" / "README.md"
        ).read_text() == "downstream README"
        # other.txt comes through from upstream untouched
        assert (
            overlay / "{{ cookiecutter.__folder_name }}" / "other.txt"
        ).read_text() == "untouched"

    def test_missing_downstream_template_uses_underlay_alone(self, tmp_path: Path):
        upstream_template = tmp_path / "upstream" / "templates" / "project"
        _write(upstream_template / "cookieplone.json", '{"upstream": true}')

        # Downstream template dir does not exist on disk
        overlay = r._build_template_overlay(
            tmp_path / "downstream" / "templates" / "project",
            underlay=[(tmp_path / "upstream", "templates/project")],
        )

        assert (overlay / "cookieplone.json").read_text() == '{"upstream": true}'

    def test_multiple_underlay_layers_layered_in_order(self, tmp_path: Path):
        c_template = tmp_path / "c" / "templates" / "project"
        _write(c_template / "file.txt", "from C")
        b_template = tmp_path / "b" / "templates" / "project"
        _write(b_template / "file.txt", "from B")
        a_template = tmp_path / "a" / "templates" / "project"
        _write(a_template / "file.txt", "from A")

        overlay = r._build_template_overlay(
            a_template,
            underlay=[
                (tmp_path / "c", "templates/project"),
                (tmp_path / "b", "templates/project"),
            ],
        )

        # A (the base / winning layer) wins
        assert (overlay / "file.txt").read_text() == "from A"
