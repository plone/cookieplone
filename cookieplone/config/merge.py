# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Merge logic for the repository ``extends`` mechanism.

Provides a pure function that combines an upstream ``cookieplone-config.json``
with a downstream one, applying the merge rules documented in issue #175:

- ``version`` / ``title`` / ``description``: downstream wins.
- ``extends``: stripped from the merged result.
- ``templates`` / ``groups``: keyed union, downstream entries replace upstream
  entries that share an ``id``.  Group ``templates`` lists are replaced
  wholesale (not appended) so downstream can re-order or drop entries.
- ``config.versions``: shallow merge, downstream wins per key.
- ``config.renderer``: downstream wins if set, otherwise upstream.
- ``config.min_version``: ``max(upstream, downstream)`` via PEP 440 ordering.

Template path resolution is supported via the top-level
``_template_origins`` sidecar mapping ``template_id`` to the absolute repo
directory the template's ``path`` is relative to.  Consumers
(``_parse_template_options``) look up origins here instead of using a single
``base_path``.

The sidecar key is prefixed with ``_`` to signal it is an internal annotation
added after schema validation.  The merged result therefore should *not* be
revalidated against the strict structural schema; only the cross-referential
checks in :func:`cookieplone.config.schemas._collect_group_errors` are
meaningful on a merged config.
"""

from __future__ import annotations

from cookieplone.exceptions import InvalidConfiguration
from copy import deepcopy
from packaging.version import Version
from pathlib import Path
from typing import Any


ORIGINS_KEY = "_template_origins"


def normalize_extends(value: Any) -> dict[str, str] | None:
    """Normalise the ``extends`` field to the canonical object form.

    Accepts either the legacy string form (``"gh:plone/cookieplone-templates"``)
    or the object form (``{"url": "...", "tag": "2.1.0"}``).  Empty strings
    and ``None`` resolve to ``None`` (no extension declared).

    :param value: Raw ``extends`` value as parsed from the config file.
    :returns: ``{"url": str, "tag": str | None}`` on success, or ``None`` when
        no extension is declared.
    :raises InvalidConfiguration: When *value* is neither a string nor an
        object with a ``url`` key.
    """
    if value is None or value == "":
        return None
    if isinstance(value, str):
        return {"url": value, "tag": None}
    if isinstance(value, dict) and "url" in value:
        return {"url": value["url"], "tag": value.get("tag")}
    raise InvalidConfiguration(
        f"'extends' must be a string or an object with a 'url' key, got: {value!r}"
    )


def _merge_min_version(upstream: str | None, downstream: str | None) -> str | None:
    """Return the stricter of two PEP 440 version strings.

    :param upstream: ``config.min_version`` from the upstream config (or
        ``None`` if unset).
    :param downstream: ``config.min_version`` from the downstream config (or
        ``None`` if unset).
    :returns: The stricter (higher) version string, or ``None`` when both
        sides are unset.
    """
    if upstream is None:
        return downstream
    if downstream is None:
        return upstream
    return upstream if Version(upstream) >= Version(downstream) else downstream


def _merge_config_section(upstream: dict, downstream: dict) -> dict:
    """Merge the ``config`` sub-section with the documented rules."""
    merged: dict[str, Any] = {}

    versions = {**upstream.get("versions", {}), **downstream.get("versions", {})}
    if versions:
        merged["versions"] = versions

    renderer = downstream.get("renderer") or upstream.get("renderer")
    if renderer:
        merged["renderer"] = renderer

    min_version = _merge_min_version(
        upstream.get("min_version"), downstream.get("min_version")
    )
    if min_version:
        merged["min_version"] = min_version

    return merged


def merge_repo_configs(
    upstream: dict[str, Any],
    downstream: dict[str, Any],
    *,
    upstream_repo_dir: Path,
    downstream_repo_dir: Path,
) -> dict[str, Any]:
    """Combine an upstream and downstream repository config.

    See the module docstring for the full merge-rules table.  Template-path
    resolution is preserved via the top-level :data:`ORIGINS_KEY` sidecar:
    every template ID in the merged ``templates`` mapping has a matching
    entry in ``result[ORIGINS_KEY]`` pointing at the repo directory its
    relative ``path`` resolves against.

    For a transitive chain (``A extends B extends C``) the *upstream*
    argument is the already-merged ``B+C`` result; its ``_template_origins``
    are preserved, so a template inherited from ``C`` keeps pointing at
    ``C``'s clone.

    :param upstream: Upstream repository config dict (may itself be a
        previously merged result).
    :param downstream: Downstream repository config dict.
    :param upstream_repo_dir: Filesystem path that *upstream*'s template
        ``path`` values resolve against.  Only used to stamp origins for
        entries that don't already carry one.
    :param downstream_repo_dir: Filesystem path that *downstream*'s template
        ``path`` values resolve against.
    :returns: The merged repository config dict, with an internal
        ``_template_origins`` mapping.
    """
    merged: dict[str, Any] = {}

    merged["version"] = downstream.get("version", upstream.get("version"))
    merged["title"] = downstream.get("title", upstream.get("title"))

    description = downstream.get("description", upstream.get("description"))
    if description is not None:
        merged["description"] = description

    upstream_origins: dict[str, str] = dict(upstream.get(ORIGINS_KEY, {}))
    upstream_templates = deepcopy(upstream.get("templates", {}))
    downstream_templates = deepcopy(downstream.get("templates", {}))

    merged_templates: dict[str, Any] = {**upstream_templates, **downstream_templates}
    merged_origins: dict[str, str] = {}
    upstream_dir_str = str(upstream_repo_dir)
    downstream_dir_str = str(downstream_repo_dir)
    for tmpl_id in merged_templates:
        if tmpl_id in downstream_templates:
            merged_origins[tmpl_id] = downstream_dir_str
        else:
            merged_origins[tmpl_id] = upstream_origins.get(tmpl_id, upstream_dir_str)
    merged["templates"] = merged_templates
    merged[ORIGINS_KEY] = merged_origins

    upstream_groups = deepcopy(upstream.get("groups", {}))
    downstream_groups = deepcopy(downstream.get("groups", {}))
    merged_groups = {**upstream_groups, **downstream_groups}
    if merged_groups:
        merged["groups"] = merged_groups

    config = _merge_config_section(
        upstream.get("config", {}), downstream.get("config", {})
    )
    if config:
        merged["config"] = config

    return merged
