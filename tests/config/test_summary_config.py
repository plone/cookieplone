"""Tests for the ``config.summary`` block of the repository config.

Covers parsing the post-generation summary settings from
``cookieplone-config.json`` (including default values when the block is
absent), schema validation, and the ``extends`` extension mechanism that
merges a downstream summary on top of an upstream one.
"""

from cookieplone._types import SignatureInfo
from cookieplone._types import SummaryInfo
from cookieplone.config.merge import merge_repo_configs
from cookieplone.config.schemas import validate_repository_config
from pathlib import Path

import json
import pytest


RESOURCES = Path(__file__).parent.parent / "_resources" / "config"

UPSTREAM_DIR = Path("upstream")
DOWNSTREAM_DIR = Path("downstream")


def _load(name: str) -> dict:
    """Load a repository config fixture by file name."""
    return json.loads((RESOURCES / name).read_text())


def _summary_of(config: dict) -> SummaryInfo:
    """Resolve a :class:`SummaryInfo` from a repository config dict, mirroring
    how :func:`cookieplone.repository._populate_repository_metadata` reads it."""
    raw = config.get("config", {}).get("summary", {})
    return SummaryInfo.from_dict(raw)


def _merge(upstream: dict, downstream: dict) -> dict:
    """Merge two repository configs the way the ``extends`` mechanism does."""
    return merge_repo_configs(
        upstream,
        downstream,
        upstream_repo_dir=UPSTREAM_DIR,
        downstream_repo_dir=DOWNSTREAM_DIR,
    )


def _repo_with_summary(summary: dict | None) -> dict:
    """Build a minimal valid repository config, optionally with a summary."""
    config: dict = {}
    if summary is not None:
        config["summary"] = summary
    return {
        "version": "1.0",
        "title": "Templates",
        "groups": {
            "main": {
                "title": "Main",
                "description": "Main templates",
                "templates": ["project"],
            }
        },
        "templates": {"project": {"path": ".", "title": "Project", "description": "D"}},
        "config": config,
    }


class TestSummaryParsing:
    """Parsing ``config.summary`` from ``cookieplone-config.json``."""

    def test_configured_values_are_read(self):
        """The fixture with a summary block yields its configured values."""
        info = _summary_of(_load("cookieplone-config.json"))
        assert info == SummaryInfo(
            enabled=True,
            message="Your Plone project is ready to roll!",
            thanks="Thanks for choosing Plone,",
            signature=SignatureInfo(
                text="The Plone Community Team",
                url="https://plone.org/community",
            ),
        )

    def test_defaults_when_block_absent(self):
        """A config without a summary block falls back to all defaults."""
        info = _summary_of(_load("cookieplone-config-no-summary.json"))
        assert info == SummaryInfo()
        assert info.enabled is False

    @pytest.mark.parametrize(
        "attr,expected",
        [
            ("enabled", False),
            (
                "message",
                "Now, code it, create a git repository, push to your organization.",
            ),
            ("thanks", "Sorry for the convenience,"),
        ],
    )
    def test_default_scalar_values(self, attr, expected):
        """Each scalar default is applied when the summary block is missing."""
        info = _summary_of(_load("cookieplone-config-no-summary.json"))
        assert getattr(info, attr) == expected

    def test_default_signature(self):
        """The default signature is applied when the summary block is missing."""
        info = _summary_of(_load("cookieplone-config-no-summary.json"))
        assert info.signature == SignatureInfo(
            text="The Plone Community", url="https://plone.org"
        )


class TestSummarySchema:
    """Schema validation of the ``config.summary`` block."""

    @pytest.mark.parametrize(
        "name",
        ["cookieplone-config.json", "cookieplone-config-no-summary.json"],
    )
    def test_fixtures_validate(self, name):
        """Both summary fixtures pass repository config validation."""
        valid, errors = validate_repository_config(_load(name))
        assert valid is True, errors

    def test_partial_summary_validates(self):
        """A summary block with only some keys is valid."""
        valid, errors = validate_repository_config(
            _repo_with_summary({"enabled": True})
        )
        assert valid is True, errors

    def test_enabled_must_be_boolean(self):
        """A non-boolean ``enabled`` is rejected by the schema."""
        valid, _errors = validate_repository_config(
            _repo_with_summary({"enabled": "yes"})
        )
        assert valid is False


class TestSummaryExtendsMerge:
    """The ``extends`` mechanism merges summary downstream-over-upstream."""

    def test_downstream_inherits_upstream_summary(self):
        """A downstream without a summary inherits the upstream's."""
        upstream = _repo_with_summary({"enabled": True, "message": "Upstream message"})
        downstream = {"version": "1.0", "title": "Downstream", "extends": "gh:up"}
        merged = _merge(upstream, downstream)
        info = _summary_of(merged)
        assert info.enabled is True
        assert info.message == "Upstream message"

    def test_downstream_overrides_per_key(self):
        """Downstream summary keys win; upstream fills the omitted keys."""
        upstream = _repo_with_summary({
            "enabled": True,
            "message": "Upstream message",
            "signature": {"text": "Upstream", "url": "https://up.example"},
        })
        downstream = {
            "version": "1.0",
            "title": "Downstream",
            "extends": "gh:up",
            "config": {"summary": {"message": "Downstream message"}},
        }
        merged = _merge(upstream, downstream)
        summary = merged["config"]["summary"]
        assert summary["message"] == "Downstream message"
        # Untouched keys come from upstream.
        assert summary["enabled"] is True
        assert summary["signature"] == {"text": "Upstream", "url": "https://up.example"}

    def test_no_summary_either_side_yields_defaults(self):
        """When neither side configures a summary, defaults apply."""
        upstream = _repo_with_summary(None)
        downstream = {"version": "1.0", "title": "Downstream", "extends": "gh:up"}
        merged = _merge(upstream, downstream)
        assert _summary_of(merged) == SummaryInfo()
