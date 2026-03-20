---
myst:
  html_meta:
    "description": "How to add a new built-in validator to the Cookieplone codebase."
    "property=og:description": "How to add a new built-in validator to the Cookieplone codebase."
    "property=og:title": "Add a validator"
    "keywords": "Cookieplone, validators, DEFAULT_VALIDATORS, contributing, cookieplone.json"
---

# Add a validator

Validators in Cookieplone check user input at prompt time.
They live in `cookieplone/validators/__init__.py` and return `bool` (`True` means the value is valid).

## Understand the contract

A validator is a plain function that accepts a single `str` value and returns `bool`:

```python
def my_validator(value: str) -> bool:
    """Return True if value passes the check."""
    return bool(value)
```

- Return `True` → the value is accepted.
- Return `False` → the prompt repeats and asks the user to try again.

## Add the validator function

Open `cookieplone/validators/__init__.py`.
Add the new function, following the existing pattern:

```python
def semver(value: str) -> bool:
    """Validate that value is a valid SemVer string (MAJOR.MINOR.PATCH)."""
    import re
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, value))
```

If the underlying logic is non-trivial, add a helper to `cookieplone/utils/validators.py` and call it from here (following the pattern of `hostname`, `python_package_name`, and others).

## Wire the validator to a field name (optional)

If the new validator applies to a field that appears in many templates by name,
add it to `DEFAULT_VALIDATORS` in `cookieplone/settings.py`:

```python
DEFAULT_VALIDATORS = {
    "plone_version": "cookieplone.validators.plone_version",
    "volto_version": "cookieplone.validators.volto_version",
    "python_package_name": "cookieplone.validators.python_package_name",
    "hostname": "cookieplone.validators.hostname",
    "language_code": "cookieplone.validators.language_code",
    "semver_field": "cookieplone.validators.semver",  # new entry
}
```

Any template field named `semver_field` then runs `semver` automatically without any extra configuration.

Template authors can also reference it explicitly via the `validator` key in `cookieplone.json`:

```json
{
  "version": "2.0",
  "properties": {
    "api_version": {
      "type": "string",
      "title": "API version",
      "default": "1.0.0",
      "validator": "cookieplone.validators.semver"
    }
  }
}
```

## Write a test

Add a test in `tests/validators/`:

```python
# tests/validators/test_semver.py
from cookieplone.validators import semver


def test_semver_valid():
    assert semver("1.2.3") is True


def test_semver_invalid_missing_patch():
    assert semver("1.2") is False


def test_semver_invalid_text():
    assert semver("latest") is False


def test_semver_empty():
    assert semver("") is False
```

Run the test:

```console
uv run pytest tests/validators/test_semver.py -v
```

## Verify the full test suite still passes

```console
make test
```

## Document the validator

Add a row for the new validator in {doc}`/reference/validators`.
Note whether it is wired into `DEFAULT_VALIDATORS`.

## Related pages

- {doc}`/reference/validators`: all built-in validators with their signatures.
- {doc}`/how-to-guides/add-validators-to-your-template`: use validators in a template.
- {doc}`/how-to-guides/set-up-dev-environment`: set up your local development environment.
- {doc}`/concepts/validators-and-filters`: how validators and filters differ.
