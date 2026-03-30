---
myst:
  html_meta:
    "description": "All built-in validators provided by Cookieplone, including the DEFAULT_VALIDATORS autowiring table."
    "property=og:description": "All built-in validators provided by Cookieplone, including the DEFAULT_VALIDATORS autowiring table."
    "property=og:title": "Validators reference"
    "keywords": "Cookieplone, validators, DEFAULT_VALIDATORS, reference, python_package_name, plone_version"
---

# Validators reference

Validators check user input at prompt time.
A validator function accepts a single string value and either returns `True` (value accepted) or raises `ValidationError` with a message describing what is wrong.

All validators are defined in `cookieplone/validators/__init__.py`.

## DEFAULT_VALIDATORS

Cookieplone automatically applies a validator to any field whose name matches a key in `DEFAULT_VALIDATORS`.
No configuration is needed in the template schema.

| Field name | Validator |
|---|---|
| `plone_version` | `cookieplone.validators.plone_version` |
| `volto_version` | `cookieplone.validators.volto_version` |
| `python_package_name` | `cookieplone.validators.python_package_name` |
| `hostname` | `cookieplone.validators.hostname` |
| `language_code` | `cookieplone.validators.language_code` |

A template can override any of these by providing an explicit `validator` key in `cookieplone.json`.

---

## Built-in validators

### `not_empty`

**Signature**: `not_empty(value: str) -> bool`

Returns `True` when the value is non-empty after stripping whitespace.

| Input | Result |
|---|---|
| `"hello"` | `True` |
| `"  "` | `False` |
| `""` | `False` |

Not in `DEFAULT_VALIDATORS`.
Reference it explicitly:

```json
{
  "project_title": {
    "type": "string",
    "title": "Project title",
    "validator": "cookieplone.validators.not_empty"
  }
}
```

---

### `language_code`

**Signature**: `language_code(value: str) -> bool`

Returns `True` when the value is a valid IETF language tag (for example `en`, `pt-BR`, `zh-CN`).

Automatically applied to fields named `language_code`.

---

### `python_package_name`

**Signature**: `python_package_name(value: str) -> bool`

Returns `True` when the value is a valid Python identifier or dotted name
(for example `myaddon`, `collective.myaddon`, `plone.app.content`).

Automatically applied to fields named `python_package_name`.

---

### `hostname`

**Signature**: `hostname(value: str) -> bool`

Returns `True` when the value is a syntactically valid hostname
(for example `example.com`, `my-server`).

Automatically applied to fields named `hostname`.

---

### `volto_addon_name`

**Signature**: `volto_addon_name(value: str) -> bool`

Returns `True` when the value is a valid Volto add-on name
(a scoped or unscoped npm package name that also satisfies Volto naming conventions).

Not in `DEFAULT_VALIDATORS`.
Reference it explicitly as `cookieplone.validators.volto_addon_name`.

---

### `npm_package_name`

**Signature**: `npm_package_name(value: str) -> bool`

Returns `True` when the value is a valid npm package name.

Not in `DEFAULT_VALIDATORS`.
Reference it explicitly as `cookieplone.validators.npm_package_name`.

---

### `plone_version`

**Signature**: `plone_version(value: str) -> bool`

Returns `True` when the value is a Plone version number of at least 6.0.

Automatically applied to fields named `plone_version`.

---

### `volto_version`

**Signature**: `volto_version(value: str) -> bool`

Returns `True` when the value is a Volto version number of at least `18.0.0-alpha.43`.

Automatically applied to fields named `volto_version`.

---

## Validation errors

When a validator rejects user input, it raises a `ValidationError` with a human-readable message.
The renderer displays the message inline so the user knows what to fix.

```python
from tui_forms.form.question import ValidationError

def my_validator(value: str) -> bool:
    if not value.startswith("plone"):
        raise ValidationError("Value must start with 'plone'.")
    return True
```

## Using a validator in a template

### In `cookieplone.json` (v2)

Set the `validator` key to the dotted import path:

```json
{
  "author_email": {
    "type": "string",
    "title": "Author email",
    "default": "",
    "validator": "cookieplone.validators.not_empty"
  }
}
```

### In `cookiecutter.json` (v1)

Add the field to `__validators__`:

```json
{
  "author_email": "",
  "__validators__": {
    "author_email": "cookieplone.validators.not_empty"
  }
}
```

## Related pages

- {doc}`/reference/schema-v2`: full v2 schema reference including the `validator` key.
- {doc}`/how-to-guides/add-validators-to-your-template`: use validators in a template.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator to Cookieplone.
- {doc}`/concepts/validators-and-filters`: how validators and filters differ.
