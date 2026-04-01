---
myst:
  html_meta:
    "description": "Reference for the legacy cookiecutter.json v1 template schema supported by cookieplone."
    "property=og:description": "Reference for the legacy cookiecutter.json v1 template schema supported by cookieplone."
    "property=og:title": "Schema v1 reference (cookiecutter.json)"
    "keywords": "Cookieplone, cookiecutter.json, schema, v1, legacy, __prompts__, __validators__"
---

# Schema v1 reference (`cookiecutter.json`)

Cookieplone supports the standard `cookiecutter.json` format (v1) for backwards compatibility.
New templates should use the v2 format (`cookieplone.json`) described in {doc}`/reference/schema-v2`.

## Basic structure

A v1 schema is a flat JSON object.
Keys are field names; values are the defaults.

```json
{
  "project_title": "My Plone Site",
  "author_name": "Plone Community",
  "port": 8080,
  "database_backend": ["postgresql", "sqlite"]
}
```

- A **string** value produces a free-text prompt.
- An **integer** value produces a numeric prompt.
- A **list** value produces a choice prompt; the first element is the default.

## Hidden fields

Keys that begin with a single underscore (`_`) are constant values.
They are not shown to the user.

```json
{
  "_schema_version": "1.0"
}
```

## Computed fields

Keys that begin with a double underscore (`__`) are computed from a Jinja2 expression.
They are not shown to the user.

```json
{
  "project_slug": "my-plone-site",
  "__package_name": "{{ cookiecutter.project_slug | replace('-', '_') }}"
}
```

## Custom prompts (`__prompts__`)

The reserved key `__prompts__` maps field names to human-readable question strings.
For choice fields, it also provides option labels.

```json
{
  "database_backend": ["postgresql", "sqlite"],
  "__prompts__": {
    "project_title": "What is the project title?",
    "database_backend": {
      "__prompt__": "Choose a database backend",
      "postgresql": "PostgreSQL (recommended)",
      "sqlite": "SQLite (development only)"
    }
  }
}
```

## Custom validators (`__validators__`)

The reserved key `__validators__` maps field names to dotted import paths of validator functions.

```json
{
  "hostname": "example.com",
  "__validators__": {
    "hostname": "cookieplone.validators.hostname"
  }
}
```

Validators declared in `DEFAULT_VALIDATORS` are applied automatically by field name and do not need to appear in `__validators__`.
See {doc}`/reference/validators`.

## Root `cookiecutter.json` for template repositories

The root of a template repository uses a special `cookiecutter.json` format with a `templates` key.
This is different from the per-template schema described above.

```json
{
  "templates": {
    "project": {
      "path": "./templates/project",
      "title": "A Plone project",
      "description": "Full Plone project with backend and frontend."
    }
  }
}
```

See {doc}`/concepts/template-repositories` for the full structure.

## Upgrade path

To upgrade a v1 schema to v2:

1. Rename `cookiecutter.json` to `cookieplone.json`.
2. Wrap the field definitions under `schema.properties` and add `schema.version: "2.0"`.
3. Move prompts from `__prompts__` into each field's `"title"` key.
4. Move validators from `__validators__` into each field's `"validator"` key.
5. Convert computed fields from `__key` to a property with `"format": "computed"`.
6. Move `_extensions` to `config.extensions`.
7. Move `_copy_without_render` to `config.no_render`.
8. Move `__cookieplone_subtemplates` to `config.subtemplates`, converting each `[id, title, enabled]` tuple to an object `{"id": "...", "title": "...", "enabled": "..."}`.
9. Move `__cookieplone_template` to the top-level `id` key.
10. Add version pins to `config.versions` as needed (accessible in templates as `{{ version.<key> }}`).

## Related pages

- {doc}`/reference/schema-v2`: the v2 `cookieplone.json` format.
- {doc}`/reference/validators`: built-in validators and autowiring by field name.
- {doc}`/concepts/template-repositories`: root `cookiecutter.json` structure.
