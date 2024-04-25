# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import requests
from packaging.version import Version

from cookieplone import settings


def get_npm_package_versions(package: str) -> list[str]:
    """Get versions for a NPM package."""
    url: str = f"https://registry.npmjs.org/{package}"
    resp = requests.get(url, headers={"Accept": "application/vnd.npm.install-v1+json"})  # noQA: S113
    data = resp.json()
    return list(data["dist-tags"].values())


def get_pypi_package_versions(package: str) -> list[str]:
    """Get versions for a PyPi package."""
    url: str = f"https://pypi.org/pypi/{package}/json"
    resp = requests.get(url)  # noQA: S113
    data = resp.json()
    return list(data.get("releases").keys())


def is_valid_version(
    version: Version,
    min_version: Version | None = None,
    max_version: Version | None = None,
    allow_prerelease: bool = False,
) -> bool:
    """Check if version is valid."""
    status = True
    if version.is_prerelease:
        status = allow_prerelease
    if status and min_version:
        status = version >= min_version
    if status and max_version:
        status = version < max_version
    return status


def latest_version(
    versions: list[str],
    min_version: str | None = None,
    max_version: str | None = None,
    allow_prerelease: bool = False,
) -> str | None:
    min_version = Version(min_version) if min_version else None
    max_version = Version(max_version) if max_version else None
    versions_ = sorted(
        [(Version(v.replace("v", "")), v) for v in versions], reverse=True
    )
    valid = [
        (version, raw_version)
        for version, raw_version in versions_
        if is_valid_version(version, min_version, max_version, allow_prerelease)
    ]
    return valid[0][1] if valid else None


def latest_volto(
    min_version: str | None = None,
    max_version: str | None = None,
    allow_prerelease: bool = False,
) -> str | None:
    """Return the latest volto version."""
    versions = get_npm_package_versions("@plone/volto")
    return latest_version(
        versions,
        min_version=min_version,
        max_version=max_version,
        allow_prerelease=allow_prerelease,
    )


def latest_plone(
    min_version: str | None = None,
    max_version: str | None = None,
    allow_prerelease: bool = False,
) -> str | None:
    """Return the latest Plone version."""
    versions = get_pypi_package_versions("Plone")
    return latest_version(
        versions,
        min_version=min_version,
        max_version=max_version,
        allow_prerelease=allow_prerelease,
    )


def node_version_for_volto(volto_version: str) -> int:
    """Return the Node Version to be used with Volto."""
    major = Version(volto_version).major
    return settings.VOLTO_NODE.get(major, settings.DEFAULT_NODE)
