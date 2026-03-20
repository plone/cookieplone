---
myst:
  html_meta:
    "description": "How to use Cookieplone's built-in Jinja2 filters inside a template."
    "property=og:description": "How to use Cookieplone's built-in Jinja2 filters inside a template."
    "property=og:title": "Use built-in filters"
    "keywords": "Cookieplone, filters, Jinja2, template, package_name, pascal_case, latest_plone"
---

# Use built-in filters

Cookieplone registers a set of Jinja2 filters that you can use in template files, computed field defaults, and any other Jinja2 expression within your template.

## Use a filter in a template file

In any Jinja2-templated file inside your template, apply a filter with the `|` operator:

```python
# {{ cookiecutter.python_package_name | pascal_case }} package
```

If `python_package_name` is `my_plone_addon`, the rendered output is:

```python
# MyPloneAddon package
```

## Use a filter in a computed field default

In `cookieplone.json`, use filters inside computed field expressions:

```json
{
  "class_name": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.python_package_name | pascal_case }}"
  },
  "namespace_path": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.python_package_name | package_namespace_path }}"
  }
}
```

## Use a filter in a directory or file name

Jinja2 expressions in directory names and file names are also rendered.
Name a directory `{{cookiecutter.python_package_name | package_path}}` and Cookieplone creates the path `src/my_namespace/my_plone_addon`.

## Available filters

See {doc}`/reference/filters` for the full list of built-in filters with signatures and examples.
The most commonly used ones include:

| Filter | Purpose |
|---|---|
| `package_name` | Last segment of a dotted package name |
| `package_namespace` | All segments except the last |
| `package_path` | Dotted name as a filesystem path under `src/` |
| `pascal_case` | Underscore-separated name in PascalCase |
| `latest_plone` | Latest released Plone version |
| `latest_volto` | Latest released Volto version |
| `python_versions` | Supported Python versions for a given Plone version |
| `as_major_minor` | Version string truncated to `major.minor` |

## Related pages

- {doc}`/reference/filters`: all built-in filters with input/output examples.
- {doc}`/how-to-guides/add-computed-fields`: use filters in computed field defaults.
- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter to Cookieplone.
- {doc}`/concepts/validators-and-filters`: how filters differ from validators.
