# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
import re
from typing import Any
from urllib.parse import urlparse

from packaging.version import InvalidVersion, Version

from cookieplone import data, settings


def _version_from_str(value: str) -> Version | None:
    """Parse a value and return a Version"""
    try:
        version = Version(value)
    except InvalidVersion:
        version = None
    return version


def validate_not_empty(value: Any, key: str = "") -> str:
    """Value should not be empty."""
    status = True
    if isinstance(value, str):
        status = bool(value.strip())
    elif isinstance(value, int | float):
        # We accept 0 as valid
        status = True
    else:
        status = bool(value)

    return "" if status else f"{key} should be provided"


def validate_component_version(component: str, version: str, min_version: str) -> str:
    """Validate if a component version is bigger than the min_version."""
    version_ = _version_from_str(version)
    min_version = _version_from_str(min_version)
    check = version_ and min_version and (version_ >= min_version)
    return "" if check else f"{version} is not a valid {component} version."


def validate_language_code(value: str) -> str:
    """Language code should be valid."""
    pattern = r"^([a-z]{2}|[a-z]{2}-[a-z]{2})$"
    return (
        "" if re.match(pattern, value) else f"'{value}' is not a valid language code."
    )


def validate_python_package_name(value: str) -> str:
    """Validate python_package_name is an identifier."""
    parts = value.split(".")
    if any(not part.isidentifier() for part in parts):
        return f"'{value}' is not a valid Python identifier."
    return ""


def validate_hostname(value: str) -> str:
    """Check if hostname is valid."""
    valid = False
    if value and value.strip():
        value_with_protocol = f"https://{value}"
        result = urlparse(value_with_protocol)
        valid = str(result.hostname) == value
    return "" if valid else f"'{value}' is not a valid hostname."


def validate_volto_addon_name(value: str) -> str:
    """Validate the volto addon name is valid."""
    pattern = "^[a-z0-9-~][a-z0-9-._~]*$"
    return "" if re.match(pattern, value) else f"'{value}' is not a valid name."


def validate_npm_package_name(value: str) -> str:
    """Validate the npm package name is valid."""
    pattern = r"^(@[a-z0-9-~][a-z0-9-._~]*\/)?[a-z0-9-~][a-z0-9-._~]*$"
    return "" if re.match(pattern, value) else f"'{value}' is not a valid package name."


def validate_plone_version(value: str) -> str:
    """Validate Plone Version."""
    version = _version_from_str(value)
    status = bool(version) and (
        version >= _version_from_str(settings.PLONE_MIN_VERSION)
    )
    return "" if status else f"{value} is not a valid Plone version."


def validate_volto_version(value: str) -> str:
    """Validate Volto Version."""
    version = _version_from_str(value)
    status = bool(version) and (
        version >= _version_from_str(settings.VOLTO_MIN_VERSION)
    )
    return "" if status else f"Volto version {value} is not supported by this template."


def run_context_validations(
    context: dict, validations: list[data.ItemValidator], allow_empty: bool = False
) -> data.ContextValidatorResult:
    """Run validations for context."""
    global_status = True
    results = []
    if not allow_empty:
        func = validate_not_empty
        for key in context:
            if key.startswith("_"):
                # Ignore computed values
                continue
            validations.append(data.ItemValidator(key, func, "error"))
    for validation in validations:
        status = False
        key = validation.key
        func = validation.func
        value = context.get(key, "")
        level = validation.level
        message = func(value, key) if func == validate_not_empty else func(value)
        if not message:
            status = True
            message = "✓"
        elif level == "warning":
            status = True
        global_status = global_status and status
        results.append(data.ItemValidatorResult(key, status, message))
    global_message = (
        f"Ran {len(results)} validations and "
        f"they {'passed' if global_status else 'failed'}."
    )
    return data.ContextValidatorResult(
        status=global_status, message=global_message, validations=results
    )
