from cookieplone.utils import validators


def not_empty(value: str) -> bool:
    """Validator to check if a value is not empty."""
    return bool(value and value.strip())


def language_code(value: str) -> bool:
    """Language code should be valid."""
    result = validators.validate_language_code(value)
    return not result


def python_package_name(value: str) -> bool:
    """Validate python_package_name is an identifier."""
    result = validators.validate_python_package_name(value)
    return not result


def hostname(value: str) -> bool:
    """Check if hostname is valid."""
    result = validators.validate_hostname(value)
    return not result


def volto_addon_name(value: str) -> bool:
    """Validate the volto addon name is valid."""
    result = validators.validate_volto_addon_name(value)
    return not result


def npm_package_name(value: str) -> bool:
    """Validate the npm package name is valid."""
    result = validators.validate_npm_package_name(value)
    return not result


def plone_version(value: str) -> bool:
    """Validate Plone Version."""
    result = validators.validate_plone_version(value)
    return not result


def volto_version(value: str) -> bool:
    """Validate Volto Version."""
    result = validators.validate_volto_version(value)
    return not result
