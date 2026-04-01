---
myst:
  html_meta:
    "description": "Full specification for the cookieplone.json v2 template schema."
    "property=og:description": "Full specification for the cookieplone.json v2 template schema."
    "property=og:title": "Schema v2 reference (cookieplone.json)"
    "keywords": "Cookieplone, cookieplone.json, schema, v2, properties, computed, choice, validator, config, extensions, versions, subtemplates"
---

# Schema v2 reference (`cookieplone.json`)

Template schemas in v2 format are stored in a file named `cookieplone.json` at the root of each sub-template directory.

## Top-level structure

A v2 file separates the **form schema** (what the user sees) from the **generator configuration** (how the template is processed).

```json
{
  "id": "project",
  "schema": {
    "title": "My template",
    "description": "A short description shown to the user.",
    "version": "2.0",
    "properties": { }
  },
  "config": {
    "extensions": [],
    "no_render": [],
    "versions": {},
    "subtemplates": []
  }
}
```

| Key | Type | Required | Description |
|---|---|---|---|
| `id` | string | no | Unique identifier for the template. |
| `schema` | object | yes | Form definition shown to the user. |
| `config` | object | no | Generator configuration (extensions, versions, etc.). |

## Schema object

The `schema` object defines the interactive form.

```json
{
  "schema": {
    "title": "My template",
    "description": "A short description shown to the user.",
    "version": "2.0",
    "properties": { }
  }
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
| `minLength` | integer | no | Minimum number of characters. |
| `maxLength` | integer | no | Maximum number of characters. |
| `pattern` | string | no | Regular expression the value must match. |

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
| `minimum` | integer | no | Minimum allowed value. |
| `maximum` | integer | no | Maximum allowed value. |

### Choice (via `oneOf`)

A single-choice field where the user selects one option.
Uses standard JSON Schema `oneOf` with `const`/`title` pairs.

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

## Configuration object

The optional `config` object holds generator settings that are **not** shown in the wizard.
These values control how Cookieplone processes the template after the user answers all questions.

```json
{
  "config": {
    "extensions": [
      "cookieplone.filters.latest_plone",
      "cookieplone.filters.latest_volto"
    ],
    "no_render": ["*.png", "devops/etc"],
    "versions": {
      "gha_checkout": "v6",
      "plone": "6.1"
    },
    "subtemplates": [
      {"id": "sub/backend", "title": "Backend", "enabled": "1"},
      {"id": "sub/frontend", "title": "Frontend", "enabled": "{{ cookiecutter.has_frontend }}"}
    ]
  }
}
```

| Key | Type | Description |
|---|---|---|
| `extensions` | array of strings | Jinja2 extension classes to load (dotted import paths). These make custom filters and tags available in template files. |
| `no_render` | array of strings | Glob patterns for files that should be copied as-is, without Jinja2 rendering. |
| `versions` | object | String-to-string mapping of version identifiers. Injected into the template context as `{{ version.<key> }}`. |
| `subtemplates` | array of objects | Sub-templates to run after the main template. Each entry has `id`, `title`, and `enabled` keys. |

All `config` keys are optional.
When a key is absent or empty, the corresponding feature is not activated.

### `extensions`

Jinja2 extension modules to load.
Each entry is a dotted Python import path pointing to a class that extends `jinja2.ext.Extension`.

```json
{
  "config": {
    "extensions": [
      "cookieplone.filters.latest_plone",
      "cookieplone.filters.pascal_case"
    ]
  }
}
```

### `no_render`

Glob patterns for files that should be copied verbatim, without Jinja2 rendering.
Use this for binary files or files whose content conflicts with Jinja2 syntax.

```json
{
  "config": {
    "no_render": ["*.png", "*.ico", "devops/etc"]
  }
}
```

### `versions`

A flat mapping of version identifiers to version strings.
These are injected into the template context as a top-level `versions` namespace, separate from the `cookiecutter` namespace.

```json
{
  "config": {
    "versions": {
      "gha_checkout": "v6",
      "plone": "6.1",
      "volto": "18.10.0"
    }
  }
}
```

In template files, reference these values with `{{ versions.gha_checkout }}`, `{{ versions.plone }}`, etc.

```{note}
Unlike other config keys, `versions` lives outside the `cookiecutter` namespace.
The full template context passed to Jinja2 looks like `{"cookiecutter": {...}, "versions": {...}}`.
```

### `subtemplates`

Sub-templates that run after the main template completes.
Each entry is an object with three required keys.

```json
{
  "config": {
    "subtemplates": [
      {"id": "sub/backend", "title": "Backend", "enabled": "1"},
      {"id": "sub/frontend", "title": "Frontend", "enabled": "{{ cookiecutter.has_frontend }}"}
    ]
  }
}
```

| Key | Type | Description |
|---|---|---|
| `id` | string | Path to the sub-template directory, relative to the template repository root. |
| `title` | string | Human-readable label shown in logs and passed to post-generation hooks. |
| `enabled` | string | Controls whether the sub-template runs. See below. |

#### The `enabled` field

The `enabled` field determines whether a sub-template is activated.
It can be a **static value** or a **Jinja2 expression**:

- **Static**: `"1"` to always enable, `"0"` to always disable.
- **Jinja2 expression**: An expression like `"{{ cookiecutter.has_frontend }}"` that is rendered against the current template context after all user answers are collected. The resolved value is passed through to the post-generation hook.

```json
{
  "config": {
    "subtemplates": [
      {"id": "sub/backend", "title": "Backend", "enabled": "1"},
      {"id": "sub/docs", "title": "Documentation", "enabled": "{{ cookiecutter.initialize_docs }}"},
      {"id": "sub/frontend", "title": "Frontend", "enabled": "{{ cookiecutter.has_frontend }}"}
    ]
  }
}
```

In this example, `sub/backend` always runs, while `sub/docs` and `sub/frontend` depend on the user's answers.

#### How subtemplates are processed

During generation, each subtemplate entry is converted into a `[id, title, enabled]` list and injected into the template context as `__cookieplone_subtemplates`.
Post-generation hooks read this list to decide which sub-templates to invoke.

The processing order matches the declaration order in the configuration file.

## Complete example

```json
{
  "id": "addon",
  "schema": {
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
  },
  "config": {
    "extensions": [
      "cookieplone.filters.latest_plone",
      "cookieplone.filters.pascal_case",
      "cookieplone.filters.package_path"
    ],
    "no_render": ["*.png"],
    "versions": {
      "gha_checkout": "v6"
    }
  }
}
```

## Wizard features

### Confirmation page

After the last question the wizard shows a summary of the answers.
The user can confirm to proceed or decline to restart the wizard with their previous answers pre-populated.

### Back-navigation

While filling in the wizard the user can type `<` at any prompt to go back to the previous question.
A hint is displayed automatically when going back is possible.

## Related pages

- {doc}`/reference/schema-v1`: legacy `cookiecutter.json` format.
- {doc}`/reference/filters`: all built-in Jinja2 filters usable in computed fields.
- {doc}`/reference/validators`: all built-in validators and the `DEFAULT_VALIDATORS` table.
- {doc}`/how-to-guides/add-computed-fields`: how to use computed fields in a template.
- {doc}`/concepts/computed-defaults`: how computed defaults are evaluated.
