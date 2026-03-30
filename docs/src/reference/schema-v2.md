---
myst:
  html_meta:
    "description": "Full specification for the cookieplone.json v2 template schema."
    "property=og:description": "Full specification for the cookieplone.json v2 template schema."
    "property=og:title": "Schema v2 reference (cookieplone.json)"
    "keywords": "Cookieplone, cookieplone.json, schema, v2, properties, computed, choice, validator"
---

# Schema v2 reference (`cookieplone.json`)

Template schemas in v2 format are stored in a file named `cookieplone.json` at the root of each sub-template directory.

## Top-level structure

```json
{
  "title": "My template",
  "description": "A short description shown to the user.",
  "version": "2.0",
  "properties": { }
}
```

| Key | Type | Required | Description |
|---|---|---|---|
| `title` | string | no | Display name shown in the wizard header. |
| `description` | string | no | Short description shown below the title. |
| `version` | string | yes | Must be `"2.0"`. |
| `properties` | object | yes | Ordered map of field definitions. |

Properties are evaluated in the order they appear in the file.
Computed fields can reference only fields that appear earlier in `properties`.

## Field types

### `string`

A free-text input field.

```json
{
  "project_title": {
    "type": "string",
    "title": "Project title",
    "description": "The human-readable name of the project.",
    "default": "My Plone Site"
  }
}
```

| Key | Type | Required | Description |
|---|---|---|---|
| `type` | `"string"` | yes | Field type. |
| `title` | string | yes | Label shown as the prompt question. |
| `description` | string | no | Additional help text shown below the prompt. |
| `default` | string | no | Default value pre-filled in the prompt. |
| `validator` | string | no | Dotted import path to a validator function. |
| `format` | string | no | Set to `"computed"` or `"constant"` for non-interactive fields. |

### `integer`

A numeric input field.

```json
{
  "port": {
    "type": "integer",
    "title": "Port number",
    "default": 8080,
    "validator": "my_template.validators.valid_port"
  }
}
```

| Key | Type | Required | Description |
|---|---|---|---|
| `type` | `"integer"` | yes | Field type. |
| `title` | string | yes | Label shown as the prompt question. |
| `default` | integer | no | Default integer value. |
| `validator` | string | no | Dotted import path to a validator function. |

### Choice (via `oneOf`)

A single-choice field where the user selects one option.
Uses standard JSONSchema `oneOf` with `const`/`title` pairs.

```json
{
  "database_backend": {
    "type": "string",
    "title": "Database backend",
    "oneOf": [
      {"const": "postgresql", "title": "PostgreSQL"},
      {"const": "sqlite", "title": "SQLite (development only)"}
    ],
    "default": "postgresql"
  }
}
```

| Key | Type | Required | Description |
|---|---|---|---|
| `type` | `"string"` | yes | Field type. |
| `title` | string | yes | Label shown as the prompt question. |
| `oneOf` | array of `{"const", "title"}` objects | yes | Available choices. Each entry has a `const` (the stored value) and a `title` (the label shown to the user). |
| `default` | string | no | The `const` of the preselected option. |
| `validator` | string | no | Dotted import path to a validator function. |

## Computed fields

A field with `"format": "computed"` is not shown to the user.
Its value is derived from a Jinja2 expression in `default`.

```json
{
  "package_name": {
    "type": "string",
    "format": "computed",
    "default": "{{ cookiecutter.project_slug | replace('-', '_') }}"
  }
}
```

The expression has access to all fields that appear earlier in `properties`.
Cookieplone's built-in filters are available (see {doc}`/reference/filters`).

## Constant fields

A field with `"format": "constant"` holds a fixed value that never changes.
It is not shown to the user and its `default` is a literal string, not a Jinja2 expression.

```json
{
  "schema_version": {
    "type": "string",
    "format": "constant",
    "default": "2.0"
  }
}
```

## Validator key

The `validator` key accepts a dotted Python import path.
The function at that path must accept a single string argument and return `bool`.

```json
{
  "hostname": {
    "type": "string",
    "title": "Server hostname",
    "default": "example.com",
    "validator": "cookieplone.validators.hostname"
  }
}
```

Fields whose names match an entry in `DEFAULT_VALIDATORS` are wired automatically.
See {doc}`/reference/validators` for the complete list.

## Complete example

```json
{
  "title": "Plone add-on",
  "description": "A minimal Plone add-on template.",
  "version": "2.0",
  "properties": {
    "python_package_name": {
      "type": "string",
      "title": "Python package name",
      "description": "Use dots for namespaces: collective.myaddon",
      "default": "collective.myaddon"
    },
    "plone_version": {
      "type": "string",
      "title": "Plone version",
      "default": "6.1.2"
    },
    "class_name": {
      "type": "string",
      "format": "computed",
      "default": "{{ cookiecutter.python_package_name | pascal_case }}"
    },
    "package_path": {
      "type": "string",
      "format": "computed",
      "default": "{{ cookiecutter.python_package_name | package_path }}"
    }
  }
}
```

## Related pages

- {doc}`/reference/schema-v1`: legacy `cookiecutter.json` format.
- {doc}`/reference/filters`: all built-in Jinja2 filters usable in computed fields.
- {doc}`/reference/validators`: all built-in validators and the `DEFAULT_VALIDATORS` table.
- {doc}`/how-to-guides/add-computed-fields`: how to use computed fields in a template.
- {doc}`/concepts/computed-defaults`: how computed defaults are evaluated.
