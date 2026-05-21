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

from collections.abc import Generator
from cookieplone.config.merge import LAYERS_KEY
from cookieplone.config.merge import normalize_extends
from cookieplone.repository import _RESOLUTION_CACHE
from cookieplone.repository import _load_raw_repository_config
from cookieplone.repository import _resolve_and_merge_extends
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
import shutil
import warnings


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
