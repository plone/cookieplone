"""Validators for the example template."""

from tui_forms.form.question import ValidationError


def no_spaces(value: str) -> bool:
    """Reject answers that contain spaces."""
    if " " in value:
        raise ValidationError("Use hyphens instead of spaces.")
    return True
