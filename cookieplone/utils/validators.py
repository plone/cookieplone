import re
from urllib.parse import urlparse

from packaging.version import InvalidVersion, Version


def _version_from_str(value: str) -> Version | None:
    """Parse a value and return a Version"""
    try:
        version = Version(value)
    except InvalidVersion:
        version = None
    return version


def validate_not_empty(key: str, value: str) -> str:
    """Value should not be empty."""
    return "" if value.strip() else f"{key} should be provided"


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
    return (
        "" if value.isidentifier() else f"'{value}' is not a valid Python identifier."
    )


def validate_hostname(value: str) -> str:
    """Check if hostname is valid."""
    valid = False
    if value and value.strip():
        value_with_protocol = f"https://{value}"
        result = urlparse(value_with_protocol)
        valid = str(result.hostname) == value
    return "" if valid else f"'{value}' is not a valid hostname."
