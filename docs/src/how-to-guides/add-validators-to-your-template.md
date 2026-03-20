---
myst:
  html_meta:
    "description": "How to add input validation to fields in a Cookieplone template."
    "property=og:description": "How to add input validation to fields in a Cookieplone template."
    "property=og:title": "Add validators to your template"
    "keywords": "Cookieplone, validators, template, cookieplone.json, DEFAULT_VALIDATORS, custom validator"
---

# Add validators to your template

Validators run when a user submits a field value during the interactive prompt.
If the validator returns `False`, the prompt stays open and asks the user to enter a valid value.

## Use a built-in validator

Cookieplone automatically wires built-in validators to fields whose names match the `DEFAULT_VALIDATORS` table.
The following field names are autowired without any configuration:

| Field name | Validator applied |
|---|---|
| `plone_version` | `cookieplone.validators.plone_version` |
| `volto_version` | `cookieplone.validators.volto_version` |
| `python_package_name` | `cookieplone.validators.python_package_name` |
| `hostname` | `cookieplone.validators.hostname` |
| `language_code` | `cookieplone.validators.language_code` |

Name your field `python_package_name` and the validator applies automatically.

## Assign a validator explicitly in `cookieplone.json`

Add a `validator` key to a field property in your `cookieplone.json`:

```json
{
  "version": "2.0",
  "properties": {
    "python_package_name": {
      "type": "string",
      "title": "Python package name",
      "default": "my_package",
      "validator": "cookieplone.validators.python_package_name"
    }
  }
}
```

The `validator` value is an import path to a callable that accepts the field value as a string and returns a boolean.

## Assign a validator in `cookiecutter.json` (v1 format)

In the v1 schema, add a `__validators__` key at the top level of `cookiecutter.json`:

```json
{
  "python_package_name": "my_package",
  "__validators__": {
    "python_package_name": "cookieplone.validators.python_package_name"
  }
}
```

## Write a custom validator

Place a Python module in your template's hook directory or in a package that is importable when Cookieplone runs.
A validator is any callable that takes a single string and returns `True` when valid and `False` when invalid.

```python
def no_spaces(value: str) -> bool:
    """Reject values that contain spaces."""
    return " " not in value
```

Reference it by its import path in your schema:

```json
{
  "validator": "myhooks.validators.no_spaces"
}
```

## Related pages

- {doc}`/reference/validators`: all built-in validators and their accepted values.
- {doc}`/concepts/validators-and-filters`: how validators and filters differ conceptually.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator to Cookieplone itself.
