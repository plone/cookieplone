# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import re
import subprocess
import sys

from cookieplone import settings


def _get_command_version(cmd: str) -> str:
    """Get the reported version of a command line utility."""
    try:
        raw_version = (
            subprocess.run([cmd, "--version"], capture_output=True)  # noQA: S603
            .stdout.decode()
            .strip()
        )
    except (FileNotFoundError, PermissionError):
        raw_version = ""
    return raw_version


def _parse_node_major_version(value: str) -> str:
    """Parse value and return the major version of Node."""
    match = re.match(r"v(\d{1,3})\.\d{1,3}.\d{1,3}", value)
    return match.groups()[0] if match else ""


def _parse_docker_version(value: str) -> str:
    """Parse value and return the docker version."""
    value = value.strip()
    match = re.match(r"Docker version (\d{2}).(\d{1,2}).(\d{1,2})", value)
    if match:
        groups = match.groups()
        return f"{groups[0]}.{groups[1]}"
    return ""


def check_python_version(supported_versions: list[str] | None = None) -> str:
    """Check if Python version is supported."""
    supported = (
        supported_versions if supported_versions else settings.SUPPORTED_PYTHON_VERSIONS
    )
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return (
        ""
        if version in supported
        else f"Python version is not supported: Got {sys.version}"
    )


def check_node_version(supported_versions: list[str] | None = None) -> str:
    """Check if node version is supported."""
    supported = (
        supported_versions if supported_versions else settings.SUPPORTED_NODE_VERSIONS
    )
    raw_version = _get_command_version("node")
    if not raw_version:
        return "NodeJS not found."
    else:
        version = _parse_node_major_version(raw_version)
        return (
            ""
            if version in supported
            else f"Node version is not supported: Got {raw_version}"
        )


def check_docker_version(min_version: str) -> str:
    """Check if docker version is supported."""
    min_version = min_version if min_version else settings.MIN_DOCKER_VERSION
    raw_version = _get_command_version("docker")
    if not raw_version:
        return "Docker not found."
    else:
        version = _parse_docker_version(raw_version)
        return (
            ""
            if version >= min_version
            else f"Docker version is not supported: Got {version}"
        )


def check_command_is_available(command: str) -> str:
    """Check if a command line utility is available."""
    raw_version = _get_command_version(command)
    return "" if raw_version else f"Command {command} is not available."
