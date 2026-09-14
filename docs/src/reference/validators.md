---
myst:
  html_meta:
    "description": "The validator contract, all built-in validators provided by Cookieplone, and the DEFAULT_VALIDATORS table."
    "property=og:description": "The validator contract, all built-in validators provided by Cookieplone, and the DEFAULT_VALIDATORS table."
    "property=og:title": "Validators reference"
    "keywords": "Cookieplone, validators, ValidationError, DEFAULT_VALIDATORS, reference, python_package_name, plone_version"
---

# Validators reference

Validators check answers in the wizard.
This page describes the contract that every validator follows, the validators that Cookieplone provides, and the fields that get a validator automatically.

All built-in validators are defined in `cookieplone/validators/__init__.py`.

(validator-contract)=

## Validator contract

A validator is a Python callable that a template references by its dotted import path, such as `cookieplone.validators.hostname`.

- **Input**: the answer, converted to a string. A boolean answer arrives as `"True"` or `"False"`.
- **Accept**: return `True`.
- **Reject with a message**: raise `ValidationError` from `tui_forms.form.question`, with a message that says what to fix. The wizard shows the message and asks the question again. All built-in validators reject this way.
- **Reject without a message**: return `False`. The wizard shows a generic error and asks the question again.

```python
from tui_forms.form.question import ValidationError


def starts_with_plone(value: str) -> bool:
    """Accept only values that start with 'plone'."""
    if not value.startswith("plone"):
        raise ValidationError("Value must start with 'plone'.")
    return True
```

### With `--no-input`

With `--no-input`, Cookieplone runs each validator on the value it would use, such as the default or a value passed as extra context.
A rejected value stops the generation with an error that includes the validator's message, for example:

```text
Default value 'My Project' for 'project_title' fails validation: 'My Project' is not a valid Python identifier.
```

### Import

Cookieplone imports every validator when it reads the template's `cookieplone.json`, before it asks any question.
A path that doesn't import stops the generation, also with `--no-input`.

The module can live in either of these places:

- A package installed in the same environment as Cookieplone, such as `cookieplone.validators`, or a package added with `uvx --with`.
- The template's directory, next to its `cookieplone.json`.
  Cookieplone appends that directory to the Python import path while it generates the template, so an installed module with the same name takes precedence.

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

A `validator` key on the field in `cookieplone.json` replaces the automatic validator.

---

## Built-in validators

Each built-in validator returns `True` for a valid value, and raises `ValidationError` with a message for an invalid one.

### `not_empty`

**Signature**: `not_empty(value: str) -> bool`

Accepts a value that is not empty after stripping whitespace.

| Input | Result |
|---|---|
| `"hello"` | accepted |
| `"  "` | rejected |
| `""` | rejected |

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

Accepts a valid IETF language tag (for example `en`, `pt-BR`, `zh-CN`).

Automatically applied to fields named `language_code`.

---

### `python_package_name`

**Signature**: `python_package_name(value: str) -> bool`

Accepts a valid Python identifier or dotted name
(for example `myaddon`, `collective.myaddon`, `plone.app.content`).

Automatically applied to fields named `python_package_name`.

---

### `hostname`

**Signature**: `hostname(value: str) -> bool`

Accepts a syntactically valid hostname
(for example `example.com`, `my-server`).

Automatically applied to fields named `hostname`.

---

### `volto_addon_name`

**Signature**: `volto_addon_name(value: str) -> bool`

Accepts a valid Volto add-on name
(a scoped or unscoped npm package name that also satisfies Volto naming conventions).

Not in `DEFAULT_VALIDATORS`.
Reference it explicitly as `cookieplone.validators.volto_addon_name`.

---

### `npm_package_name`

**Signature**: `npm_package_name(value: str) -> bool`

Accepts a valid npm package name.

Not in `DEFAULT_VALIDATORS`.
Reference it explicitly as `cookieplone.validators.npm_package_name`.

---

### `plone_version`

**Signature**: `plone_version(value: str) -> bool`

Accepts a Plone version number of at least 6.0.

Automatically applied to fields named `plone_version`.

---

### `volto_version`

**Signature**: `volto_version(value: str) -> bool`

Accepts a Volto version number of at least `18.0.0-alpha.43`.

Automatically applied to fields named `volto_version`.

---

## Using a validator in a template

Set the `validator` key of a property in `cookieplone.json` to the dotted import path:

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

## Related pages

- {doc}`/reference/schema-v2`: full v2 schema reference including the `validator` key.
- {doc}`/how-to-guides/add-validators-to-your-template`: use validators in a template.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator to Cookieplone.
- {doc}`/concepts/validators-and-filters`: how validators and filters differ.
