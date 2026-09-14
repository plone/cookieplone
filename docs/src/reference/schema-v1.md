---
myst:
  html_meta:
    "description": "Reference for the legacy cookiecutter.json v1 format, which Cookieplone 2.0 does not support, with steps to migrate to cookieplone.json."
    "property=og:description": "Reference for the legacy cookiecutter.json v1 format, which Cookieplone 2.0 does not support, with steps to migrate to cookieplone.json."
    "property=og:title": "Schema v1 reference (cookiecutter.json)"
    "keywords": "Cookieplone, cookiecutter.json, schema, v1, legacy, migration, __prompts__, __validators__"
---

# Schema v1 reference (`cookiecutter.json`)

```{important}
Cookieplone 2.0 does not support the v1 format, neither for templates nor for the root of a template repository.
This page describes the format only to help you migrate to {doc}`/reference/schema-v2` and {doc}`/reference/repository-config`.
```

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

## Migrate a template to v2

To migrate a template's `cookiecutter.json` to `cookieplone.json`:

1. Rename `cookiecutter.json` to `cookieplone.json`.
2. Add a top-level `id` with the template ID, and move `__cookieplone_template` there if the file has it.
3. Move the fields under `schema.properties`, and add `schema.version: "2.0"`.
   Turn each field into an object with `type`, `title`, and `default`.
4. Move prompts from `__prompts__` into each field's `title`, and choice labels into `oneOf` entries.
5. Move validators from `__validators__` into each field's `validator` key.
6. Turn `__key` computed fields into properties with `"format": "computed"`, and `_key` constants into properties with `"format": "constant"`.
7. Move `_extensions` to `config.extensions`, and list every Cookieplone filter the template uses there.
8. Move `_copy_without_render` to `config.no_render`.
9. Move `__cookieplone_subtemplates` to `config.subtemplates`, converting each `[id, title, enabled]` list to an object `{"id": "...", "title": "...", "enabled": "..."}`.
10. Add version pins to `config.versions` as needed, and reference them in template files as `{{ versions.<key> }}`.

(schema-v1-legacy-root)=

## Migrate a repository's root `cookiecutter.json`

Before 2.0, the root of a template repository could hold a `cookiecutter.json` with a `templates` key:

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

To migrate it to `cookieplone-config.json`:

1. Rename the file to `cookieplone-config.json`.
2. Add `"version": "1.0"` and a `title` for the repository.
3. Add `groups`, and assign every template to exactly one group.

See {doc}`/concepts/template-repositories` for the structure of the result.

## Related pages

- {doc}`/reference/schema-v2`: the v2 `cookieplone.json` format.
- {doc}`/reference/repository-config`: the `cookieplone-config.json` format.
- {doc}`/reference/validators`: built-in validators and automatic validators by field name.
