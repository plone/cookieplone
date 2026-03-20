---
myst:
  html_meta:
    "description": "An explanation of how Cookieplone validators and Jinja2 filters differ, when each runs, and how DEFAULT_VALIDATORS auto-wires by field name."
    "property=og:description": "An explanation of how Cookieplone validators and Jinja2 filters differ, when each runs, and how DEFAULT_VALIDATORS auto-wires by field name."
    "property=og:title": "Validators and filters"
    "keywords": "Cookieplone, validators, filters, Jinja2, DEFAULT_VALIDATORS, autowiring, prompt time"
---

# Validators and filters

Validators and filters both process field values, but they run at different points in the pipeline and serve different purposes.

## Validators

A validator is a function that checks whether a user's answer meets a constraint.
It runs at **prompt time**, immediately after the user submits an answer.

- **Input**: the raw string the user typed.
- **Output**: `bool` (`True` means the answer is accepted; `False` means the prompt repeats).
- **Effect**: a rejected answer causes Cookieplone to ask the question again until the value is valid.

Validators enforce correctness—they prevent invalid data from entering the template context.

### Example

The `python_package_name` validator checks that the value is a valid Python identifier or dotted name:

```python
def python_package_name(value: str) -> bool:
    """Validate python_package_name is an identifier."""
    result = validators.validate_python_package_name(value)
    return not result
```

If you type `my-addon` (with a hyphen), the prompt repeats.
If you type `my_addon`, the answer is accepted and the wizard moves on.

### Autowiring with DEFAULT_VALIDATORS

Cookieplone maintains a table of field names mapped to validators.
Any field whose name appears in this table is validated automatically—no configuration in the template schema is needed.

| Field name | Validator applied |
|---|---|
| `plone_version` | `cookieplone.validators.plone_version` |
| `volto_version` | `cookieplone.validators.volto_version` |
| `python_package_name` | `cookieplone.validators.python_package_name` |
| `hostname` | `cookieplone.validators.hostname` |
| `language_code` | `cookieplone.validators.language_code` |

A template can override any autowired validator by providing an explicit `validator` key in `cookieplone.json`.

## Filters

A filter is a Jinja2 function that transforms a value.
It runs at **render time**: after the wizard has collected all answers, when Cookiecutter renders the template files.

- **Input**: any value already in the template context.
- **Output**: a transformed value (string, integer, or list).
- **Effect**: the rendered output in files, filenames, or computed defaults reflects the transformed value.

Filters shape data—they convert raw answers into the exact form needed in the generated output.

### Example

The `pascal_case` filter converts an underscore-separated name to PascalCase:

```python
@simple_filter
def pascal_case(package_name: str) -> str:
    """Return the package name as a string in the PascalCase format."""
    parts = [name.title() for name in package_name.split("_")]
    return "".join(parts)
```

In a template file:

```python
# {{ cookiecutter.python_package_name | pascal_case }}
```

If `python_package_name` is `collective.myaddon`, the rendered line becomes:

```python
# Collective.Myaddon
```

## Key differences

| Aspect | Validator | Filter |
|---|---|---|
| When it runs | Prompt time (after user types) | Render time (after all answers collected) |
| Input | Raw user input string | Any template context value |
| Output | `bool` (accept or reject) | Transformed value |
| Purpose | Reject invalid answers | Convert values for use in files |
| Configured in | `validator` key or `DEFAULT_VALIDATORS` | `|` operator in Jinja2 expressions |
| User sees result? | Indirectly (rejected prompts) | In generated files |

## Using both together

Validators and filters often work together on the same field.

The `python_package_name` field uses `python_package_name` (validator) to ensure the value is a valid Python identifier,
then uses `pascal_case` (filter) in computed fields and template files to derive a class name:

```json
{
  "python_package_name": {
    "type": "string",
    "title": "Python package name",
    "default": "collective.myaddon"
  },
  "class_name": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.python_package_name | pascal_case }}"
  }
}
```

The validator runs first (at prompt time) to ensure the value is valid.
The filter runs later (at render time) to produce the derived class name.

## Related pages

- {doc}`/reference/validators`: all built-in validators and the DEFAULT_VALIDATORS table.
- {doc}`/reference/filters`: all built-in Jinja2 filters with examples.
- {doc}`/how-to-guides/add-validators-to-your-template`: wire validators to template fields.
- {doc}`/how-to-guides/use-built-in-filters`: use filters in template files and computed fields.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator.
- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter.
