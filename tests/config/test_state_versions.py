"""Tests for version merging in cookieplone.config.state."""

from cookieplone.config import state as config
from cookieplone.config.v2 import ParsedConfig

import pytest


@pytest.mark.parametrize(
    "global_versions,template_versions,expected",
    [
        (None, {}, {}),
        ({"traefik": "v2.11"}, {}, {"traefik": "v2.11"}),
        (None, {"plone": "6.1"}, {"plone": "6.1"}),
        ({}, {"plone": "6.1"}, {"plone": "6.1"}),
        (
            {"traefik": "v2.11"},
            {"plone": "6.1"},
            {"traefik": "v2.11", "plone": "6.1"},
        ),
        (
            {"gha_checkout": "v6", "traefik": "v2.11"},
            {"gha_checkout": "v7"},
            {"gha_checkout": "v7", "traefik": "v2.11"},
        ),
    ],
    ids=[
        "both_empty",
        "global_only",
        "template_only",
        "empty_global_dict",
        "disjoint_keys",
        "template_overrides_global",
    ],
)
def test_merge_versions(global_versions, template_versions, expected):
    assert config._merge_versions(global_versions, template_versions) == expected


@pytest.mark.parametrize(
    "template_versions,global_versions,expected_versions",
    [
        (
            {"gha_checkout": "v6", "plone": "6.1"},
            None,
            {"gha_checkout": "v6", "plone": "6.1"},
        ),
        ({}, None, {}),
        (
            {},
            {"gha_checkout": "v6", "traefik": "v2.11"},
            {"gha_checkout": "v6", "traefik": "v2.11"},
        ),
        (
            {"gha_checkout": "v7"},
            {"gha_checkout": "v6", "traefik": "v2.11"},
            {"gha_checkout": "v7", "traefik": "v2.11"},
        ),
        ({"plone": "6.1"}, None, {"plone": "6.1"}),
    ],
    ids=[
        "template_versions_only",
        "no_versions",
        "global_versions_only",
        "template_overrides_global",
        "global_none_passthrough",
    ],
)
def test_generate_state_versions(template_versions, global_versions, expected_versions):
    parsed = ParsedConfig(
        schema={"version": "2.0", "properties": {}},
        versions=template_versions,
    )
    state = config._generate_state(parsed, global_versions=global_versions)
    assert state.data["versions"] == expected_versions
    assert state.versions == expected_versions
