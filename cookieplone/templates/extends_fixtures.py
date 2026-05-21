# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Pytest fixtures for testing downstream repositories that use the
cookieplone ``extends`` mechanism.

Auto-discovered by pytest via the ``cookieplone_extends`` entry point
under ``[project.entry-points.pytest11]``.  Downstream repos get these
fixtures for free as soon as ``cookieplone`` is a test dependency.

See :doc:`/how-to-guides/test-an-extending-repository` for usage.
"""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Generator
from cookieplone.config.merge import LAYERS_KEY
from cookieplone.config.merge import normalize_extends
from cookieplone.repository import _RESOLUTION_CACHE
from cookieplone.repository import _load_raw_repository_config
from cookieplone.repository import _parse_template_options
from cookieplone.repository import _resolve_and_merge_extends
from cookieplone.templates.bake import Result
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import os
import pytest
import shutil
import subprocess
import sys
import warnings


@dataclass
class SubprocessBakeResult:
    """Captured result of a :func:`bake_in_subprocess` invocation.

    :ivar exit_code: Process exit code.  ``0`` on success.
    :ivar stdout: Captured standard output.
    :ivar stderr: Captured standard error.
    :ivar output_dir: The directory passed to ``-o``; project (if any)
        is created inside.
    """

    exit_code: int
    stdout: str
    stderr: str
    output_dir: Path


CLI_UPSTREAM_DIR = "--cookieplone-upstream-dir"
CLI_KEEP_UPSTREAM = "--cookieplone-keep-upstream"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the ``--cookieplone-upstream-dir`` and
    ``--cookieplone-keep-upstream`` options.

    Called by pytest at collection time.  Options live in the
    ``cookieplone-extends`` group so they're discoverable via
    ``pytest --help``.
    """
    group = parser.getgroup("cookieplone-extends")
    group.addoption(
        CLI_UPSTREAM_DIR,
        action="store",
        default=None,
        dest="cookieplone_upstream_dir",
        help=(
            "Filesystem path to a local checkout of the upstream repository. "
            "When set, skip the clone declared in the downstream's 'extends' "
            "and use this directory instead. Useful when developing against "
            "an unpushed upstream branch or when running offline."
        ),
    )
    group.addoption(
        CLI_KEEP_UPSTREAM,
        action="store_true",
        default=False,
        dest="cookieplone_keep_upstream",
        help=(
            "Do not delete the resolved upstream clone at session end. "
            "Useful when debugging a failing merge."
        ),
    )


@pytest.fixture(scope="session")
def downstream_repo_dir() -> Path:
    """Local directory of the downstream repository being tested.

    Defaults to the current working directory.  Override this fixture
    when your ``cookieplone-config.json`` lives in a subdirectory.

    :returns: Resolved absolute path to the downstream repo root.
    """
    return Path.cwd().resolve()


@pytest.fixture(scope="session")
def upstream_checkout() -> str | None:
    """Optional git ref to pin the upstream to.

    Overrides whatever the downstream's ``extends.tag`` says, including
    the case where the downstream pins no tag at all.  Defaults to
    ``None`` (use the downstream's declared tag).  Override in CI
    matrices that test against multiple upstream versions.

    :returns: Git ref to pin the upstream to, or ``None`` to use the
        downstream's declared tag.
    """
    return None


@pytest.fixture(scope="session")
def upstream_repo_dir(
    request: pytest.FixtureRequest,
    downstream_repo_dir: Path,
    upstream_checkout: str | None,
) -> Generator[Path | None, None, None]:
    """Local directory of the (immediate) upstream repository.

    Session-scoped: the upstream is resolved (and cloned if necessary)
    once per session and reused across tests.  Populates
    :data:`cookieplone.repository._RESOLUTION_CACHE` so other fixtures
    that call :func:`~cookieplone.repository.get_repository_config` for
    the same downstream do not trigger a second clone.

    Behaviour:

    - When the CLI flag ``--cookieplone-upstream-dir`` is set, the
      fixture yields that path verbatim and skips resolution entirely.
    - When ``upstream_checkout`` is set, the resolver uses that git
      ref instead of the downstream's ``extends.tag``.
    - When the downstream has no ``extends``, a warning is emitted and
      ``None`` is yielded.  Tests should ``pytest.skip()`` in that case.
    - At session end the clone is removed unless
      ``--cookieplone-keep-upstream`` is set.

    :returns: Resolved local path to the immediate upstream, or ``None``
        when the downstream has no ``extends``.
    """
    forced = request.config.getoption("cookieplone_upstream_dir", default=None)
    if forced:
        yield Path(forced).resolve()
        return

    try:
        raw = _load_raw_repository_config(downstream_repo_dir)
    except RuntimeError as exc:
        warnings.warn(
            f"upstream_repo_dir: could not load downstream config at "
            f"{downstream_repo_dir}: {exc}",
            stacklevel=2,
        )
        yield None
        return

    extends = raw.get("extends") if isinstance(raw, dict) else None
    if not extends:
        warnings.warn(
            f"upstream_repo_dir: downstream config at {downstream_repo_dir} "
            f"declares no 'extends'; fixture yielded None.",
            stacklevel=2,
        )
        yield None
        return

    if upstream_checkout is not None:
        normalized = normalize_extends(extends)
        if normalized is None:
            warnings.warn(
                "upstream_repo_dir: downstream 'extends' is empty after "
                "normalisation; fixture yielded None.",
                stacklevel=2,
            )
            yield None
            return
        extends = {"url": normalized["url"], "tag": upstream_checkout}

    downstream_key = str(downstream_repo_dir.resolve())
    merged, cleanup_paths, upstream_repos = _resolve_and_merge_extends(
        downstream_config=raw,
        downstream_repo_dir=downstream_repo_dir.resolve(),
        extends=extends,
        no_input=True,
    )
    _RESOLUTION_CACHE[downstream_key] = (merged, cleanup_paths, upstream_repos)

    if not upstream_repos:
        warnings.warn(
            "upstream_repo_dir: resolution produced no upstream repos. "
            "The downstream declares 'extends' but its merged config "
            "references no inherited templates.",
            stacklevel=2,
        )
        yield None
    else:
        yield upstream_repos[0]

    keep = request.config.getoption("cookieplone_keep_upstream", default=False)
    if not keep:
        for path in cleanup_paths:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        _RESOLUTION_CACHE.pop(downstream_key, None)


@pytest.fixture
def merged_repository_config(
    downstream_repo_dir: Path,
    upstream_repo_dir: Path | None,
) -> dict[str, Any] | None:
    """The fully-merged ``cookieplone-config.json`` dict.

    Reads the cached merge result populated by
    :func:`upstream_repo_dir`.  When the downstream declares no
    ``extends`` (in which case ``upstream_repo_dir`` is ``None``), the
    raw downstream config is returned unchanged — useful so a downstream
    can write the same assertions whether or not extension is in play.

    Returns a deep copy so tests may mutate the result freely without
    affecting other tests.

    .. note::

       Does **not** honour ``--cookieplone-upstream-dir``: that flag is
       a short-circuit for ``upstream_repo_dir`` only, and the merged
       view it would produce is undefined.  Use the ``upstream_checkout``
       fixture override to pin a specific upstream tag.

    :returns: The merged config dict (downstream-wins, transitive
        layers folded in), or ``None`` when no config can be loaded.
    """
    cache_key = str(downstream_repo_dir.resolve())
    cached = _RESOLUTION_CACHE.get(cache_key)
    if cached is not None:
        return deepcopy(cached[0])
    try:
        return _load_raw_repository_config(downstream_repo_dir)
    except RuntimeError:
        return None


@pytest.fixture
def template_layers(
    merged_repository_config: dict[str, Any] | None,
) -> dict[str, list[list[str]]]:
    """The ``_template_layers`` sidecar from the merged config.

    Each value is the upstream-first list of ``(repo_dir, path)`` pairs
    that contribute to a template id.  When the downstream has no
    ``extends`` the sidecar is absent and an empty dict is returned.

    Use this fixture to assert layer order without depending on internal
    merge function names (the sidecar is a stable public contract).

    :returns: Mapping of template id to its layer stack; empty when no
        merge took place.
    """
    if merged_repository_config is None:
        return {}
    return deepcopy(merged_repository_config.get(LAYERS_KEY, {}))


@pytest.fixture
def bake_from_local(
    downstream_repo_dir: Path,
    upstream_repo_dir: Path | None,
    merged_repository_config: dict[str, Any] | None,
    tmp_path: Path,
) -> Callable[..., Result]:
    """Factory fixture that bakes a project from the downstream repo.

    Drives :func:`cookieplone.generator.generate` in-process so the
    test exercises the exact same code path the CLI uses, including
    extends-aware template-file overlay.  The upstream is whatever
    :func:`upstream_repo_dir` resolved, so a single session-scoped
    clone backs every bake.

    Output goes to *pytest*'s per-test ``tmp_path`` by default.  Pass
    ``output_dir`` to redirect.

    Usage::

        def test_bake_project(bake_from_local):
            result = bake_from_local(
                "project",
                extra_context={"title": "My Site"},
            )
            assert result.exit_code == 0
            assert result.project_path.is_dir()

    :returns: A callable
        ``(template_id, extra_context=None, output_dir=None) -> Result``.
        ``Result`` is :class:`cookieplone.templates.bake.Result` — exposes
        ``exit_code``, ``exception``, and ``project_path``.
    """
    # Import lazily so users who never touch this fixture don't pay
    # for the generator import chain.
    from cookieplone._types import GenerateConfig
    from cookieplone.generator import generate

    def _bake(
        template_id: str,
        extra_context: dict[str, Any] | None = None,
        output_dir: Path | None = None,
    ) -> Result:
        if merged_repository_config is None:
            raise RuntimeError(
                f"bake_from_local: no repository config found at "
                f"{downstream_repo_dir}; cannot bake."
            )
        templates = _parse_template_options(
            downstream_repo_dir, merged_repository_config, all_=True
        )
        if template_id not in templates:
            raise KeyError(
                f"Template {template_id!r} not found. Available: {sorted(templates)}"
            )
        tmpl = templates[template_id]

        cache_key = str(downstream_repo_dir.resolve())
        cached = _RESOLUTION_CACHE.get(cache_key)
        cached_upstreams = list(cached[2]) if cached is not None else []

        out_dir = output_dir if output_dir is not None else tmp_path
        out_dir.mkdir(parents=True, exist_ok=True)

        config = GenerateConfig(
            repository=tmpl.origin or downstream_repo_dir,
            template_name=tmpl.name,
            output_dir=out_dir,
            no_input=True,
            extra_context=extra_context,
            template_path=str(tmpl.path),
            template_underlay=tmpl.underlay or None,
            upstream_repos=cached_upstreams or None,
            dump_answers=False,
        )

        exception: BaseException | None = None
        exit_code = 0
        project_dir: Path | None = None
        try:
            project_dir = generate(config)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 0
            if code != 0:
                exception = e
            exit_code = code
        except Exception as e:
            exception = e
            exit_code = -1

        return Result(
            _project_dir=project_dir,
            exception=exception,
            exit_code=exit_code,
        )

    return _bake


@pytest.fixture
def bake_in_subprocess(
    downstream_repo_dir: Path,
    upstream_repo_dir: Path | None,
    tmp_path: Path,
) -> Callable[..., SubprocessBakeResult]:
    """Factory: bake via the installed ``cookieplone`` CLI in a subprocess.

    Opt-in variant of :func:`bake_from_local` for end-to-end smoke tests
    that want to exercise the real entry point rather than the in-process
    API.  Slower than :func:`bake_from_local`; reach for it when an
    in-process test wouldn't catch the bug (CLI argument parsing,
    environment handling, packaging issues).

    Invokes ``python -m cookieplone`` with ``--no-input``, ``-o output_dir``,
    and ``COOKIEPLONE_REPOSITORY`` set to the downstream repo.  Extra CLI
    arguments (a template id positional, ``EXTRA_CONTEXT`` ``key=value``
    pairs, or other flags) are appended verbatim.

    Usage::

        def test_smoke(bake_in_subprocess):
            result = bake_in_subprocess(
                "project",                  # template id within the repo
                "title=My Site",
                "__folder_name=site",
            )
            assert result.exit_code == 0

    :returns: A callable
        ``(*cli_args, output_dir=None, env=None, timeout=120)
            -> SubprocessBakeResult``.
    """

    def _bake(
        *cli_args: str,
        output_dir: Path | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = 120,
    ) -> SubprocessBakeResult:
        out_dir = output_dir if output_dir is not None else tmp_path / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            "-m",
            "cookieplone",
            "--no-input",
            "-o",
            str(out_dir),
            *cli_args,
        ]
        merged_env = {
            **os.environ,
            "COOKIEPLONE_REPOSITORY": str(downstream_repo_dir),
            **(env or {}),
        }
        run = subprocess.run(  # noqa: S603 — args are caller-controlled in tests
            cmd,
            capture_output=True,
            text=True,
            env=merged_env,
            timeout=timeout,
            check=False,
        )
        return SubprocessBakeResult(
            exit_code=run.returncode,
            stdout=run.stdout,
            stderr=run.stderr,
            output_dir=out_dir,
        )

    return _bake
