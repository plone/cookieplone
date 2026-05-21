# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Merge logic for the repository ``extends`` mechanism.

Provides a pure function that combines an upstream ``cookieplone-config.json``
with a downstream one, applying the merge rules documented in issue #175:

- ``version`` / ``title`` / ``description``: downstream wins.
- ``extends``: stripped from the merged result.
- ``templates``: keyed union; for an id present in both, entries are merged
  **per field** with downstream winning per field.  A downstream entry that
  omits ``path`` is a metadata-only redeclare (e.g. pure ``"hidden": true``)
  and the template files still come from upstream.
- ``groups``: keyed union, downstream entries replace upstream entries that
  share an ``id``.  Group ``templates`` lists are replaced wholesale (not
  appended) so downstream can re-order or drop entries.
- ``config.versions``: shallow merge, downstream wins per key.
- ``config.renderer``: downstream wins if set, otherwise upstream.
- ``config.min_version``: ``max(upstream, downstream)`` via PEP 440 ordering.

Template path resolution and file-overlay are both supported via the
top-level ``_template_layers`` sidecar.  For each merged template id it
holds an ordered list of ``(origin_repo_dir, path)`` pairs — upstream-first,
downstream-last.  The last entry is the *winning* origin (where the merged
manifest entry's ``path`` resolves against); the prior entries form an
underlay used by the generator at render time to overlay downstream files
on top of an upstream template tree, so a downstream can override a single
file (e.g. ``README.md``) without copying the entire upstream template.

A second sidecar, ``_template_origins`` mapping ``template_id`` to the
winning origin repo directory, is also written for the convenience of
consumers that only need the winning origin.  It is derived from
``_template_layers`` and kept consistent with it.

The sidecar keys are prefixed with ``_`` to signal they are internal
annotations added after schema validation.  The merged result should *not*
be revalidated against the strict structural schema; only the
cross-referential checks in
:func:`cookieplone.config.schemas._collect_group_errors` are meaningful on
a merged config.
"""

from __future__ import annotations

from collections import OrderedDict
from cookieplone.exceptions import InvalidConfiguration
from copy import deepcopy
from packaging.version import Version
from pathlib import Path
from typing import Any


LAYERS_KEY = "_template_layers"
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


def _initial_layers(
    upstream: dict[str, Any], upstream_repo_dir: Path
) -> dict[str, list[list[str]]]:
    """Return the upstream's ``_template_layers`` map, freshly stamped for any
    upstream template that doesn't already carry one.

    For a top-level upstream the sidecar is absent — every template's layers
    list starts as ``[[upstream_repo_dir, path]]``.  For a transitive merge
    where *upstream* is itself a merge result, the existing layers list is
    preserved so origin information from deeper layers survives.
    """
    existing = upstream.get(LAYERS_KEY, {})
    fallback_dir = str(upstream_repo_dir)
    layers: dict[str, list[list[str]]] = {}
    for tmpl_id, entry in upstream.get("templates", {}).items():
        if existing.get(tmpl_id):
            layers[tmpl_id] = [list(layer) for layer in existing[tmpl_id]]
        else:
            layers[tmpl_id] = [[fallback_dir, entry["path"]]]
    return layers


def merge_repo_configs(
    upstream: dict[str, Any],
    downstream: dict[str, Any],
    *,
    upstream_repo_dir: Path,
    downstream_repo_dir: Path,
) -> dict[str, Any]:
    """Combine an upstream and downstream repository config.

    See the module docstring for the full merge-rules table.

    Template entries are merged **per field** when an id exists in both
    upstream and downstream — downstream wins per field, with upstream
    filling fields the downstream omits.  This means a downstream may
    declare ``{"id": {"hidden": true}}`` (no ``path`` / ``title`` /
    ``description``) and inherit everything else from upstream.  The
    downstream's layer is appended to ``_template_layers`` only when
    downstream supplies ``path``; metadata-only redeclares leave the
    underlying file source on upstream.

    For a transitive chain (``A extends B extends C``) the *upstream*
    argument is the already-merged ``B+C`` result; its layers and origins
    are preserved, so a template inherited from ``C`` keeps pointing at
    ``C``'s clone.

    :param upstream: Upstream repository config dict (may itself be a
        previously merged result).
    :param downstream: Downstream repository config dict.
    :param upstream_repo_dir: Filesystem path that *upstream*'s template
        ``path`` values resolve against.  Only used to stamp layers for
        entries that don't already carry one.
    :param downstream_repo_dir: Filesystem path that *downstream*'s template
        ``path`` values resolve against.
    :returns: The merged repository config dict, with the
        ``_template_layers`` and ``_template_origins`` sidecars.
    """
    merged: dict[str, Any] = {}

    merged["version"] = downstream.get("version", upstream.get("version"))
    merged["title"] = downstream.get("title", upstream.get("title"))

    description = downstream.get("description", upstream.get("description"))
    if description is not None:
        merged["description"] = description

    upstream_templates = deepcopy(upstream.get("templates", {}))
    downstream_templates = deepcopy(downstream.get("templates", {}))
    layers = _initial_layers(upstream, upstream_repo_dir)
    downstream_dir_str = str(downstream_repo_dir)

    merged_templates: dict[str, Any] = {}
    for tmpl_id, ups_entry in upstream_templates.items():
        merged_templates[tmpl_id] = dict(ups_entry)

    for tmpl_id, ds_entry in downstream_templates.items():
        if tmpl_id in merged_templates:
            # Per-field union: downstream wins per field, upstream fills gaps.
            merged_templates[tmpl_id] = {**merged_templates[tmpl_id], **ds_entry}
            # Only append a new layer when downstream actually supplies a path.
            if "path" in ds_entry:
                layers.setdefault(tmpl_id, []).append([
                    downstream_dir_str,
                    ds_entry["path"],
                ])
        else:
            merged_templates[tmpl_id] = dict(ds_entry)
            if "path" in ds_entry:
                layers[tmpl_id] = [[downstream_dir_str, ds_entry["path"]]]

    merged["templates"] = merged_templates
    merged[LAYERS_KEY] = layers
    merged[ORIGINS_KEY] = {
        tmpl_id: tmpl_layers[-1][0]
        for tmpl_id, tmpl_layers in layers.items()
        if tmpl_layers
    }

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


def merge_template_configs(upstream: dict[str, Any], downstream: dict[str, Any]) -> dict[str, Any]:
    """Combine two template-level configuration dicts (cookieplone.json).

    - ``id``: downstream wins.
    - ``schema``: title/description/version from downstream; properties merged
      shallowly (downstream wins per key).
    - ``config``: shallow merge for versions; union of lists for extensions and
      no_render; subtemplates merged keyed by ID.
    """
    merged = deepcopy(upstream)

    if "id" in downstream:
        merged["id"] = downstream["id"]

    # Merge schema
    ups_schema = merged.setdefault("schema", {})
    ds_schema = downstream.get("schema", {})
    for field in ("title", "description", "version"):
        if field in ds_schema:
            ups_schema[field] = ds_schema[field]

    ups_props = ups_schema.setdefault("properties", {})
    ds_props = ds_schema.get("properties", {})
    ups_props.update(deepcopy(ds_props))

    # Merge config
    ups_config = merged.setdefault("config", {})
    ds_config = downstream.get("config", {})

    for list_field in ("extensions", "no_render"):
        if list_field in ds_config:
            existing = ups_config.get(list_field, [])
            ups_config[list_field] = list(OrderedDict.fromkeys(existing + ds_config[list_field]))

    if "versions" in ds_config:
        ups_config.setdefault("versions", {}).update(ds_config["versions"])

    if "subtemplates" in ds_config:
        # Keyed union of subtemplates by ID
        ups_subs = {s["id"]: s for s in ups_config.get("subtemplates", [])}
        for ds_sub in ds_config["subtemplates"]:
            ups_subs[ds_sub["id"]] = ds_sub
        ups_config["subtemplates"] = list(ups_subs.values())

    return merged
