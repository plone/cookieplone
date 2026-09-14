"""Build the inventory of the official Cookieplone templates.

The template reference pages under ``docs/src/reference/templates/`` are written
from this inventory, never from memory.  For every visible template declared in
the templates repository's ``cookieplone-config.json``, the script:

1. copies the template's ``cookieplone.json`` to ``<id>.schema.json``;
2. generates the template with ``cookieplone <id> --no-input`` in a work
   directory;
3. writes the generated directory tree to ``<id>.tree.txt``.

``index.json`` records the templates repository commit and, per template, the
exit code, duration, and generated folder name.

Run it from the repository root::

    uv run python docs/_checks/inventory_templates.py --templates-repo ../templates

Without ``--templates-repo`` the script clones
``https://github.com/plone/cookieplone-templates`` at ``--ref`` (default
``next``).  Generated projects are kept only when ``--work-dir`` is given.
"""

from pathlib import Path

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time


TEMPLATES_URL = "https://github.com/plone/cookieplone-templates"
# Tool caches depend on which formatters ran on the machine, not on the template.
SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


def render_tree(root: Path, depth: int) -> str:
    """Render *root* as a ``tree``-style listing, *depth* levels deep.

    Hidden entries are listed, except the directories in :data:`SKIP_DIRS`.
    Entries are sorted case-insensitively; directories end with ``/``.

    :param root: Directory to render.
    :param depth: Maximum number of levels below *root*.
    :returns: The listing, starting with the name of *root*.
    """
    lines = [f"{root.name}/"]

    def walk(path: Path, prefix: str, level: int) -> None:
        entries = sorted(
            (entry for entry in path.iterdir() if entry.name not in SKIP_DIRS),
            key=lambda entry: entry.name.lower(),
        )
        for index, entry in enumerate(entries):
            last = index == len(entries) - 1
            is_dir = entry.is_dir() and not entry.is_symlink()
            connector = "└── " if last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}{'/' if is_dir else ''}")
            if is_dir and level < depth:
                walk(entry, prefix + ("    " if last else "│   "), level + 1)

    walk(root, "", 1)
    return "\n".join(lines) + "\n"


def clone_templates(ref: str, destination: Path) -> Path:
    """Clone the official templates repository at *ref*.

    :param ref: Branch or tag to check out.
    :param destination: Directory to clone into.
    :returns: *destination*.
    """
    subprocess.run(  # noqa: S603
        ["git", "clone", "--quiet", "--branch", ref, TEMPLATES_URL, str(destination)],  # noqa: S607
        check=True,
    )
    return destination


def git_head(repo: Path) -> str:
    """Return the commit checked out in *repo*.

    :param repo: Path to a git repository.
    :returns: The full commit hash.
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],  # noqa: S607
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def generate(
    template_id: str, repo: Path, workdir: Path, timeout: int
) -> tuple[int, float, Path | None]:
    """Generate *template_id* from *repo* without prompting.

    Cookieplone runs with a configuration file that keeps its clone and replay
    directories inside *workdir*, so the user's home directory is not touched.
    The combined output is saved as ``cookieplone.log`` in *workdir*.

    :param template_id: Template id from ``cookieplone-config.json``.
    :param repo: Local templates repository.
    :param workdir: Empty directory for configuration, output, and logs.
    :param timeout: Seconds before the run is aborted.
    :returns: The exit code (``-1`` on timeout), the duration in seconds, and
        the generated folder, or ``None`` when there is not exactly one.
    """
    config_file = workdir / "cookieplone-config.yaml"
    config_file.write_text(
        f"cookiecutters_dir: {workdir / 'cookiecutters'}\n"
        f"replay_dir: {workdir / 'replay'}\n"
    )
    output_dir = workdir / "output"
    output_dir.mkdir()
    env = {**os.environ, "COOKIEPLONE_REPOSITORY": str(repo)}
    env.pop("COOKIEPLONE_REPOSITORY_TAG", None)
    command = [
        sys.executable,
        "-m",
        "cookieplone",
        template_id,
        "--no-input",
        "--config-file",
        str(config_file),
        "--output-dir",
        str(output_dir),
    ]
    start = time.monotonic()
    try:
        result = subprocess.run(  # noqa: S603
            command,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        returncode, log = result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = -1
        # The captured output can be bytes even with text=True.
        parts = [
            part.decode(errors="replace") if isinstance(part, bytes) else part or ""
            for part in (exc.stdout, exc.stderr)
        ]
        log = "".join(parts) + f"\nTimed out after {timeout}s\n"
    seconds = round(time.monotonic() - start, 1)
    (workdir / "cookieplone.log").write_text(log)
    generated = [entry for entry in output_dir.iterdir() if entry.is_dir()]
    return returncode, seconds, generated[0] if len(generated) == 1 else None


def main() -> int:
    """Run the inventory and return the process exit code."""
    parser = argparse.ArgumentParser(description="Inventory the official templates.")
    parser.add_argument(
        "--templates-repo", type=Path, help="Local checkout of cookieplone-templates."
    )
    parser.add_argument(
        "--ref", default="next", help="Branch or tag to clone without --templates-repo."
    )
    parser.add_argument(
        "--output", type=Path, default=Path("docs/_templates-inventory")
    )
    parser.add_argument(
        "--work-dir", type=Path, help="Keep generated projects and logs here."
    )
    parser.add_argument(
        "--only", nargs="*", default=[], help="Template ids (default: all visible)."
    )
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="cookieplone-inventory-") as tmp:
        base = (args.work_dir or Path(tmp)).resolve()
        base.mkdir(parents=True, exist_ok=True)
        if args.templates_repo:
            repo = args.templates_repo.resolve()
        else:
            repo = clone_templates(args.ref, Path(tmp) / "templates")
        repo_config = json.loads((repo / "cookieplone-config.json").read_text())
        templates = {
            template_id: data
            for template_id, data in repo_config["templates"].items()
            if not data.get("hidden", False)
            and (not args.only or template_id in args.only)
        }

        args.output.mkdir(parents=True, exist_ok=True)
        index_file = args.output / "index.json"
        index = json.loads(index_file.read_text()) if index_file.exists() else {}
        index["_source"] = {"repository": TEMPLATES_URL, "commit": git_head(repo)}

        for template_id, data in templates.items():
            print(f"==> {template_id}", flush=True)
            template_dir = repo / data["path"]
            schema = json.loads((template_dir / "cookieplone.json").read_text())
            schema_file = args.output / f"{template_id}.schema.json"
            schema_file.write_text(json.dumps(schema, indent=2) + "\n")

            workdir = base / template_id
            if workdir.exists():
                shutil.rmtree(workdir)
            workdir.mkdir()
            returncode, seconds, generated = generate(
                template_id, repo, workdir, args.timeout
            )
            tree_file = args.output / f"{template_id}.tree.txt"
            if generated:
                tree_file.write_text(render_tree(generated, args.depth))
            index[template_id] = {
                "title": data.get("title", ""),
                "path": data["path"],
                "exit_code": returncode,
                "seconds": seconds,
                "generated_folder": generated.name if generated else None,
            }
            print(f"    exit={returncode} seconds={seconds}", flush=True)
        index_file.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")

    failed = [
        key
        for key, entry in index.items()
        if not key.startswith("_") and entry["exit_code"] != 0
    ]
    if failed:
        print(f"Failed: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
