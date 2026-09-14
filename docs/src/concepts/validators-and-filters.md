---
myst:
  html_meta:
    "description": "An explanation of how Cookieplone validators and Jinja2 filters differ, when each runs, and how templates enable them."
    "property=og:description": "An explanation of how Cookieplone validators and Jinja2 filters differ, when each runs, and how templates enable them."
    "property=og:title": "Validators and filters"
    "keywords": "Cookieplone, validators, filters, Jinja2, DEFAULT_VALIDATORS, config.extensions, ValidationError"
---

# Validators and filters

Validators and filters both work on field values, but they run at different moments and serve different purposes.
A validator decides whether Cookieplone accepts an answer.
A filter transforms a value when Cookieplone renders a Jinja2 expression.

## Validators

A validator is a Python function that checks whether an answer meets a constraint.
It runs when the user submits an answer in the wizard.
With `--no-input`, it runs on the values Cookieplone would use instead, such as the defaults.

- **Input**: the answer, converted to a string.
- **Output**: `True` accepts the answer. Raising `ValidationError` rejects it with a message; returning `False` rejects it with a generic error.
- **Effect**: in the wizard, a rejected answer shows the error, and Cookieplone asks the question again. With `--no-input`, a rejected value stops the generation.

Validators enforce correctness: they keep invalid data out of the template context.
See {ref}`validator-contract` for the complete contract.

### Example

The `python_package_name` validator rejects values that aren't valid dotted Python names:

```python
def python_package_name(value: str) -> bool:
    """Validate python_package_name is an identifier."""
    result = validators.validate_python_package_name(value)
    if result:
        raise ValidationError(result)
    return True
```

If you type `my-addon` (with a hyphen), Cookieplone shows the error and asks again.
If you type `my_addon`, it accepts the answer and moves on.

### Automatic validators

Cookieplone keeps a table of field names mapped to validators, `DEFAULT_VALIDATORS`.
A field whose name appears in this table gets its validator without any configuration in the template:

| Field name | Validator applied |
|---|---|
| `plone_version` | `cookieplone.validators.plone_version` |
| `volto_version` | `cookieplone.validators.volto_version` |
| `python_package_name` | `cookieplone.validators.python_package_name` |
| `hostname` | `cookieplone.validators.hostname` |
| `language_code` | `cookieplone.validators.language_code` |

A `validator` key on the property in `cookieplone.json` replaces the automatic validator.

## Filters

A filter is a Jinja2 function that transforms a value.
A template enables each Cookieplone filter it uses by listing it in `config.extensions` of its `cookieplone.json`.

Filters run whenever Cookieplone renders a Jinja2 expression:

- in the wizard, when it renders defaults and computed fields;
- during generation, when it renders file contents, file names, and directory names.

- **Input**: a value, usually an answer from the template context.
- **Output**: a transformed value, such as a string or a list.
- **Effect**: computed fields and generated files contain the transformed value.

Filters shape data: they convert raw answers into the exact form needed in the generated output.

### Example

The `pascal_case` filter converts an underscore-separated name to PascalCase:

```python
@simple_filter
def pascal_case(package_name: str) -> str:
    """Return the package name as a string in the PascalCase format ."""
    parts = [name.title() for name in package_name.split("_")]
    return "".join(parts)
```

With `cookieplone.filters.pascal_case` in `config.extensions`, a template file can contain:

```text
# {{ cookiecutter.python_package_name | pascal_case }}
```

If `python_package_name` is `collective.myaddon`, the rendered line becomes:

```text
# Collective.Myaddon
```

## Key differences

| Aspect | Validator | Filter |
|---|---|---|
| When it runs | When an answer is submitted, or on the values used with `--no-input` | Whenever a Jinja2 expression is rendered: in the wizard and during generation |
| Input | The answer as a string | Any value in the template context |
| Output | Accept or reject | A transformed value |
| Purpose | Reject invalid answers | Convert values for use in computed fields and files |
| Configured in | The `validator` key, or automatically by field name | `config.extensions`, then the pipe operator in Jinja2 expressions |
| What the user sees | An error message and the question again | The transformed value in the generated files |

## Using both together

Validators and filters often work on the same field.
The `python_package_name` field gets the `python_package_name` validator automatically, which keeps the value a valid Python name.
A computed field then derives a class name from it with filters:

```json
{
  "schema": {
    "version": "2.0",
    "properties": {
      "python_package_name": {
        "type": "string",
        "title": "Python package name",
        "default": "collective.example_addon"
      },
      "class_name": {
        "type": "string",
        "format": "computed",
        "default": "{{ cookiecutter.python_package_name | package_name | pascal_case }}"
      }
    }
  },
  "config": {
    "extensions": [
      "cookieplone.filters.package_name",
      "cookieplone.filters.pascal_case"
    ]
  }
}
```

The validator runs first, when the user answers the question.
The filters run after all questions are answered, when Cookieplone computes `class_name`, which is `ExampleAddon` for the default answer.

## Related pages

- {doc}`/reference/validators`: the validator contract and all built-in validators.
- {doc}`/reference/filters`: all built-in Jinja2 filters with examples.
- {doc}`/how-to-guides/add-validators-to-your-template`: add validators to template fields.
- {doc}`/how-to-guides/use-built-in-filters`: enable and use filters in a template.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator.
- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter.
