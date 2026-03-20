---
myst:
  html_meta:
    "description": "How to add a new built-in Jinja2 filter to the Cookieplone codebase."
    "property=og:description": "How to add a new built-in Jinja2 filter to the Cookieplone codebase."
    "property=og:title": "Add a filter"
    "keywords": "Cookieplone, filters, Jinja2, simple_filter, contributing, Cookiecutter"
---

# Add a filter

Filters in Cookieplone are Jinja2 filters registered automatically for every template.
They live in `cookieplone/filters/__init__.py` and use the `@simple_filter` decorator from `cookiecutter.utils`.

## Understand the decorator

The `@simple_filter` decorator wraps a single-argument function and registers it as a Jinja2 filter with the same name as the function:

```python
from cookiecutter.utils import simple_filter


@simple_filter
def my_filter(value: str) -> str:
    """Return the transformed value."""
    return value.upper()
```

Template authors then call it as `{{ cookiecutter.some_field | my_filter }}`.

## Add the filter function

Open `cookieplone/filters/__init__.py` and add your function at the end of the file.
Follow the existing style:

```python
@simple_filter
def reverse_string(v: str) -> str:
    """Return the string reversed."""
    return v[::-1]
```

Rules:

- Use a single parameter named `v` for simple string-in / string-out filters,
  or a descriptive name that matches the conceptual input (see `pascal_case(package_name)` for an example).
- Add a one-line docstring that describes what the filter returns.
- Return a concrete type: `str`, `int`, or `list[str]`.
  Never return `None`.

## Write a test

Add a test in `tests/filters/` (create the file if it does not exist yet).
Name the test file after the filter or the logical group it belongs to:

```python
# tests/filters/test_string_filters.py
from cookieplone.filters import reverse_string


def test_reverse_string():
    assert reverse_string("hello") == "olleh"


def test_reverse_string_empty():
    assert reverse_string("") == ""
```

Run the test:

```console
uv run pytest tests/filters/test_string_filters.py -v
```

## Verify the full test suite still passes

```console
make test
```

## Document the filter

Add a row for the new filter in {doc}`/reference/filters`.
Include the function name, input type, output type, and an example.

## Related pages

- {doc}`/reference/filters`: all built-in filters with input/output examples.
- {doc}`/how-to-guides/set-up-dev-environment`: set up your local development environment.
- {doc}`/concepts/validators-and-filters`: how filters differ from validators.
