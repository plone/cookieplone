---
myst:
  html_meta:
    "description": "How to enable and use Cookieplone's built-in Jinja2 filters inside a template."
    "property=og:description": "How to enable and use Cookieplone's built-in Jinja2 filters inside a template."
    "property=og:title": "Use built-in filters"
    "keywords": "Cookieplone, filters, Jinja2, template, config.extensions, package_name, pascal_case, latest_plone"
---

# Use built-in filters

Cookieplone ships Jinja2 filters for the names, paths, and versions that Plone projects need.
A template enables the filters it uses, then applies them in computed fields and in file contents, file names, and directory names.

The examples on this page come from the example repository `docs/_examples/template-features/` in the Cookieplone source tree.

## Enable filters

In your template's `cookieplone.json`, list each filter under `config.extensions`, as `cookieplone.filters.` followed by the filter name:

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

Cookieplone loads the listed filters for the wizard and for rendering the template files.
A filter that is missing from the list stops the generation with an error such as `No filter named 'pascal_case'.`

## Use a filter in a file

Apply a filter to a value with the `|` operator:

```text
- Namespace: `{{ cookiecutter.python_package_name | package_namespace }}`
```

If `python_package_name` is `collective.example_addon`, the rendered line is:

```text
- Namespace: `collective`
```

Filters can be chained.
`{{ cookiecutter.python_package_name | package_name | pascal_case }}` renders as `ExampleAddon`.

## Use a filter in a computed field

In `cookieplone.json`, apply filters in the `default` of a computed field:

```json
{
  "package_path": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.python_package_name | package_path }}"
  }
}
```

See {doc}`/how-to-guides/add-computed-fields`.

## Use a filter in a directory name

Cookieplone renders file and directory names too.
To keep names readable, compute the value once, and use the computed field in the name.
The example template contains this file:

```text
{{ cookiecutter.project_slug }}/src/{{ cookiecutter.package_path }}/__init__.py
```

With the default answers, Cookieplone generates `example-addon/src/collective/example_addon/__init__.py`.
The slash in the rendered value creates nested directories.

## Commonly used filters

| Filter | Input | Output |
|---|---|---|
| `package_name` | `collective.example_addon` | `example_addon` |
| `package_namespace` | `collective.example_addon` | `collective` |
| `package_path` | `collective.example_addon` | `collective/example_addon` |
| `package_namespace_path` | `collective.example_addon` | `src/collective` |
| `pascal_case` | `example_addon` | `ExampleAddon` |
| `latest_plone` | `Yes` or `No`: whether to consider prereleases | The latest Plone version |
| `latest_volto` | `Yes` or `No`: whether to consider prereleases | The latest Volto version |

The templates in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) call the version filters with an answer, as in `{{ cookiecutter.use_prerelease_versions | latest_plone }}`.
See {doc}`/reference/filters` for every filter.

## Related pages

- {doc}`/reference/filters`: all built-in filters with input and output examples.
- {doc}`/how-to-guides/add-computed-fields`: use filters in computed field defaults.
- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter to Cookieplone.
- {doc}`/concepts/validators-and-filters`: how filters differ from validators.
