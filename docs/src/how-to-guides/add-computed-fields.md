---
myst:
  html_meta:
    "description": "How to add computed fields to a Cookieplone template that derive their value from other fields."
    "property=og:description": "How to add computed fields to a Cookieplone template that derive their value from other fields."
    "property=og:title": "Add computed fields"
    "keywords": "Cookieplone, computed fields, constant fields, Jinja2, cookieplone.json, format computed, template"
---

# Add computed fields

A computed field is a property that the wizard never asks about.
Cookieplone renders its `default` as a Jinja2 expression and stores the result with the other answers, so template files use it like any answer.

The examples on this page come from the example repository `docs/_examples/template-features/` in the Cookieplone source tree.

## Define a computed field

In your template's `cookieplone.json`, set `"format": "computed"` on a property, and write the expression in `default`:

```json
{
  "docs_enabled": {
    "type": "string",
    "format": "computed",
    "default": "{{ '1' if cookiecutter.has_docs else '0' }}"
  }
}
```

Expressions reach the answers through the `cookiecutter` namespace, for example `cookiecutter.has_docs`.

## Use filters in computed fields

A computed field can transform an answer with a filter:

```json
{
  "package_path": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.python_package_name | package_path }}"
  }
}
```

Cookieplone's filters are not available by default.
List each filter that the template uses in `config.extensions`:

```json
{
  "config": {
    "extensions": [
      "cookieplone.filters.package_name",
      "cookieplone.filters.package_namespace",
      "cookieplone.filters.package_path",
      "cookieplone.filters.pascal_case"
    ]
  }
}
```

A filter that is missing from the list stops the generation with an error such as `No filter named 'pascal_case'.`
See {doc}`/how-to-guides/use-built-in-filters`.

## Order computed fields

Cookieplone asks all visible questions first.
Then it computes the hidden fields in the order they appear in `properties`.
A computed field can use every answer to a visible question, and the computed fields that appear before it:

```json
{
  "package_path": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.python_package_name | package_path }}"
  },
  "module_path": {
    "type": "string",
    "format": "computed",
    "default": "src/{{ cookiecutter.package_path }}"
  }
}
```

A reference to a computed field that appears later renders as an empty string, without an error.
Check the order when a computed value comes out empty.

## Add a constant field

A property with `"format": "constant"` is hidden too, but Cookieplone uses its `default` as-is and doesn't render it:

```json
{
  "generator": {
    "type": "string",
    "format": "constant",
    "default": "example-templates 1.0"
  }
}
```

## Check the result

The example template defines the computed and constant fields above:

```{literalinclude} ../../_examples/template-features/my-templates/templates/features/cookieplone.json
:language: json
```

Its `README.md` uses them:

```{literalinclude} ../../_examples/template-features/my-templates/templates/features/{{ cookiecutter.project_slug }}/README.md
:language: text
```

With the default answers, the generated `README.md` contains:

```{literalinclude} ../../_examples/template-features/expected/example-addon/README.md
:language: markdown
```

## Related pages

- {doc}`/reference/schema-v2`: full `cookieplone.json` schema reference.
- {doc}`/reference/filters`: all built-in Jinja2 filters.
- {doc}`/concepts/computed-defaults`: how computed defaults are evaluated.
