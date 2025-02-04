# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import os

from cookiecutter.utils import simple_filter

from cookieplone.cli import parse_boolean
from cookieplone.utils import containers, versions


@simple_filter
def package_name(v) -> str:
    """Return the Python package name (without namespace)."""
    return v.split(".")[-1]


@simple_filter
def package_namespace(v) -> str:
    """Return the Python package namespace."""
    parts = v.rsplit(".", 1)
    if len(parts) > 1:
        return parts[0]
    return ""


@simple_filter
def package_namespaces(v) -> str:
    """Return Python package namespaces formatted for setup.py."""
    result = []
    nsparts = []
    for ns in v.split(".")[:-1]:
        nsparts.append(ns)
        result.append(".".join(nsparts))
    return ", ".join(f'"{item}"' for item in result)


@simple_filter
def package_path(v) -> str:
    """Return path to the package code within the src directory."""
    return "/".join(v.split("."))


@simple_filter
def pascal_case(package_name: str) -> str:
    """Return the package name as a string in the PascalCase format ."""
    parts = [name.title() for name in package_name.split("_")]
    return "".join(parts)


@simple_filter
def extract_host(hostname: str) -> str:
    """Get the host part of a hostname."""
    parts = hostname.split(".")
    return parts[0]


@simple_filter
def use_prerelease_versions(_: str) -> str:
    """Should we use prerelease versions of packages."""
    use_prerelease_versions = "USE_PRERELEASE" in os.environ
    return "Yes" if use_prerelease_versions else "No"


@simple_filter
def latest_volto(use_prerelease_versions: str) -> str:
    """Return the latest released version of Volto."""
    allow_prerelease = parse_boolean(use_prerelease_versions)
    return versions.latest_volto(allow_prerelease=allow_prerelease)


@simple_filter
def latest_plone(use_prerelease_versions: str) -> str:
    """Return the latest released version of Plone."""
    allow_prerelease = parse_boolean(use_prerelease_versions)
    return versions.latest_plone(allow_prerelease=allow_prerelease)


@simple_filter
def node_version_for_volto(volto_version: str) -> int:
    """Return the Node Version to be used."""
    return versions.node_version_for_volto(volto_version)


@simple_filter
def gs_language_code(code: str) -> str:
    """Return the language code as expected by Generic Setup."""
    gs_code = code.lower()
    if "-" in code:
        base_language, country = code.split("-")
        gs_code = f"{base_language}-{country.lower()}"
    return gs_code


@simple_filter
def locales_language_code(code: str) -> str:
    """Return the language code as expected by gettext."""
    gs_code = code.lower()
    if "-" in code:
        base_language, country = code.split("-")
        gs_code = f"{base_language}_{country.upper()}"
    return gs_code


@simple_filter
def image_prefix(registry: str) -> str:
    """Return the a prefix to be used with all Docker images."""
    return containers.image_prefix(registry)
