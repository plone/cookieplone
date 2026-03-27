---
myst:
  html_meta:
    "description": "How to add computed fields to a Cookieplone template that derive their value from other fields."
    "property=og:description": "How to add computed fields to a Cookieplone template that derive their value from other fields."
    "property=og:title": "Add computed fields"
    "keywords": "Cookieplone, computed fields, Jinja2, cookieplone.json, format computed, template"
---

# Add computed fields

Computed fields derive their value from other fields using Jinja2 expressions.
They are never shown to the user as prompts; Cookieplone calculates their values automatically.

## Define a computed field in `cookieplone.json`

Set `"format": "computed"` on the field and write a Jinja2 expression as the `default` value:

```json
{
  "version": "2.0",
  "properties": {
    "project_slug": {
      "type": "string",
      "title": "Project slug",
      "default": "my-project"
    },
    "package_name": {
      "type": "string",
      "format": "computed",
      "default": "{{ cookiecutter.project_slug | replace('-', '_') }}"
    }
  }
}
```

The field `package_name` is computed from `project_slug` after the user answers the prompt.
It is available to template files and to other fields that reference it.

## Reference other computed fields

Computed fields can reference previously computed fields as long as they appear later in the `properties` object:

```json
{
  "properties": {
    "project_slug": {
      "type": "string",
      "default": "my-project"
    },
    "package_name": {
      "type": "string",
      "format": "computed",
      "default": "{{ cookiecutter.project_slug | replace('-', '_') }}"
    },
    "module_path": {
      "type": "string",
      "format": "computed",
      "default": "src/{{ cookiecutter.package_name }}"
    }
  }
}
```

## Use built-in filters in computed fields

Cookieplone's built-in filters are available in Jinja2 expressions:

```json
{
  "class_name": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.package_name | pascal_case }}"
  }
}
```

See {doc}`/reference/filters` for the full list of available filters.

## Constant fields

Fields with `"format": "constant"` are similar to computed fields but are also hidden from prompts.
Use them for values that are fixed regardless of user input:

```json
{
  "schema_version": {
    "type": "string",
    "format": "constant",
    "default": "2.0"
  }
}
```

## Related pages

- {doc}`/reference/schema-v2`: full `cookieplone.json` schema reference.
- {doc}`/reference/filters`: all built-in Jinja2 filters.
- {doc}`/concepts/computed-defaults`: how computed defaults are evaluated.
