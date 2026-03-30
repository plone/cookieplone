from tui_forms.form.question import ValidationError

from cookieplone.utils import validators


def not_empty(value: str) -> bool:
    """Validator to check if a value is not empty."""
    result = validators.validate_not_empty(value)
    if result:
        raise ValidationError(result)
    return True


def language_code(value: str) -> bool:
    """Language code should be valid."""
    result = validators.validate_language_code(value)
    if result:
        raise ValidationError(result)
    return True


def python_package_name(value: str) -> bool:
    """Validate python_package_name is an identifier."""
    result = validators.validate_python_package_name(value)
    if result:
        raise ValidationError(result)
    return True


def hostname(value: str) -> bool:
    """Check if hostname is valid."""
    result = validators.validate_hostname(value)
    if result:
        raise ValidationError(result)
    return True


def volto_addon_name(value: str) -> bool:
    """Validate the volto addon name is valid."""
    result = validators.validate_volto_addon_name(value)
    if result:
        raise ValidationError(result)
    return True


def npm_package_name(value: str) -> bool:
    """Validate the npm package name is valid."""
    result = validators.validate_npm_package_name(value)
    if result:
        raise ValidationError(result)
    return True


def plone_version(value: str) -> bool:
    """Validate Plone Version."""
    result = validators.validate_plone_version(value)
    if result:
        raise ValidationError(result)
    return True


def volto_version(value: str) -> bool:
    """Validate Volto Version."""
    result = validators.validate_volto_version(value)
    if result:
        raise ValidationError(result)
    return True
