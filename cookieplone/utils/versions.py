# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import re

import requests
import semver
from packaging.version import Version

from cookieplone import settings

VERSION_PATTERNS = (
    (r"^(a)(\d{1,2})", r"alpha.\2"),
    (r"^(b)(\d{1,2})", r"beta.\2"),
    (r"^(rc)(\d{1,2})", r"rc.\2"),
)


def convert_pep440_semver(version: str) -> str:
    """Converts a PEP 440 version into a SemVer version

    :param ver: the PyPI version
    :return: a SemVer version
    """
    pypi_version = Version(version)
    pre = None if not pypi_version.pre else "".join([str(i) for i in pypi_version.pre])
    if pre:
        for raw_pattern, replace in VERSION_PATTERNS:
            pattern = re.compile(raw_pattern)
            if re.search(pattern, pre):
                pre = re.sub(pattern, replace, pre)

    parts = list(pypi_version.release)
    if len(parts) == 2:
        parts.append(0)
    major, minor, patch = parts
    build = ""
    if pypi_version.dev is not None:
        build = f"dev-{pypi_version.dev}"
    elif pypi_version.post is not None:
        build = f"post-{pypi_version.post}"
    version = str(semver.Version(major, minor, patch, prerelease=pre, build=build))
    return version


def get_npm_package_versions(package: str) -> list[str]:
    """Get versions for a npm package."""
    url: str = f"https://registry.npmjs.org/{package}"
    resp = requests.get(  # noQA: S113
        url, headers={"Accept": "application/vnd.npm.install-v1+json"}
    )
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


def version_latest(
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
    return version_latest(
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
    return version_latest(
        versions,
        min_version=min_version,
        max_version=max_version,
        allow_prerelease=allow_prerelease,
    )


def node_version_for_volto(volto_version: str) -> int:
    """Return the Node.js version to use with Volto."""
    major = Version(volto_version).major
    return settings.VOLTO_NODE.get(major, settings.DEFAULT_NODE)


def python_versions_for_plone(plone_version: str) -> settings.PythonVersionSupport:
    """Return the Python version information for a given Plone version."""
    major = Version(plone_version).major
    minor = Version(plone_version).minor
    version = f"{major}.{minor}"
    return settings.PLONE_PYTHON.get(version)


def python_version_for_plone(plone_version: str) -> str:
    """Return the latest supported Python version for a given Plone version."""
    version_support = python_versions_for_plone(plone_version)
    return version_support.latest


def format_as_major_minor(version: str) -> str:
    """Format a list of versions as major.minor."""
    # Handle "versions" used in tests / constraints
    if "-" in version:
        version = version.split("-")[0]
    v = Version(version)
    return f"{v.major}.{v.minor}"
