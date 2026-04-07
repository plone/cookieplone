---
myst:
  html_meta:
    "description": "Full specification for the cookieplone-config.json repository configuration file."
    "property=og:description": "Full specification for the cookieplone-config.json repository configuration file."
    "property=og:title": "Repository configuration (cookieplone-config.json)"
    "keywords": "Cookieplone, cookieplone-config.json, repository, templates, groups, versions, extends"
---

# Repository configuration (`cookieplone-config.json`)

The `cookieplone-config.json` file lives at the root of a template repository.
It declares the available templates, organizes them into groups for display, and provides global configuration shared across all templates.

## Top-level structure

```json
{
  "version": "1.0",
  "title": "Plone Community Templates",
  "description": "Official Cookieplone templates for the Plone community",
  "extends": "",
  "groups": { },
  "templates": { },
  "config": { }
}
```

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `version` | string | yes | Schema version. Must be `"1.0"`. |
| `title` | string | yes | Human-readable name for the template repository. |
| `description` | string | no | Short description of the repository. |
| `extends` | string | no | Repository to inherit templates from (see {ref}`repo-extends`). |
| `groups` | object | no | Template groups for the selection menu (see {ref}`repo-groups`). |
| `templates` | object | yes | Template definitions (see {ref}`repo-templates`). |
| `config` | object | no | Global configuration shared by all templates (see {ref}`repo-config`). |

(repo-templates)=
## `templates`

A mapping of template IDs to template entry objects.
Each key is a unique identifier used to reference the template from the CLI, groups, and sub-template hooks.

```json
{
  "templates": {
    "project": {
      "path": "./templates/projects/monorepo",
      "title": "Volto Project",
      "description": "Create a new Plone project that uses the Volto frontend",
      "hidden": false
    },
    "sub/cache": {
      "path": "./templates/sub/cache",
      "title": "Cache settings",
      "description": "Sub-template with cache settings.",
      "hidden": true
    }
  }
}
```

### Template entry fields

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `path` | string | yes | | Relative path from the repository root to the template directory. |
| `title` | string | yes | | Human-readable label shown in the selection menu. |
| `description` | string | yes | | Short description of what the template generates. |
| `hidden` | boolean | no | `false` | When `true`, the template is excluded from the default menu. |

Hidden templates can still be invoked directly by name:

```console
cookieplone sub/cache
```

Or made visible with `--all`:

```console
cookieplone --all
```

(repo-groups)=
## `groups`

Groups organize templates into categories for the selection menu.
Each key is a unique group identifier.

```json
{
  "groups": {
    "projects": {
      "title": "Projects",
      "description": "Generators that create a new Plone project",
      "templates": ["project", "classic_project"],
      "hidden": false
    },
    "sub": {
      "title": "Sub-Templates",
      "description": "Templates used only for internal purposes",
      "templates": ["sub/cache", "sub/frontend_project"],
      "hidden": true
    }
  }
}
```

### Group entry fields

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `title` | string | yes | | Human-readable label for the group category. |
| `description` | string | yes | | Short description of the group. |
| `templates` | array of strings | yes | | Ordered list of template IDs. Must not be empty. |
| `hidden` | boolean | no | `false` | When `true`, the group is excluded from the default menu. |

### Validation constraints

- Every template ID in a group must match a key in the top-level `templates` mapping.
- A template must not appear in more than one group.
- Every template must be assigned to at least one group.

(repo-config)=
## `config`

Global configuration shared across all templates in the repository.

```json
{
  "config": {
    "versions": {
      "gha_version_checkout": "v6",
      "gha_version_setup_node": "v4",
      "frontend_pnpm": "10.20.0"
    },
    "renderer": "rich"
  }
}
```

### `config.versions`

A flat mapping of version identifiers to version strings.
These values are available in all templates via the `versions` Jinja2 namespace:

```jinja
{{ versions.gha_version_checkout }}
```

Individual templates can override specific version values through their own `config.versions` in `cookieplone.json`.
Template-level values take precedence over repository-level values for the same key.

See {doc}`/reference/schema-v2` for details on the per-template `config.versions`.

### `config.renderer`

Selects which `tui_forms` renderer is used by the wizard for interactive runs in this repository.
Valid values are the renderer names registered with `tui_forms`: `cookiecutter` (default), `rich`, and `stdlib`.

```json
{
  "config": {
    "renderer": "rich"
  }
}
```

The `COOKIEPLONE_RENDERER` environment variable takes precedence over this field, so end-users can override the repository preference on a per-run basis.
The `--no-input` flag always forces the `noinput` renderer regardless of either setting.

If the configured renderer name is not registered with `tui_forms`, Cookieplone aborts with an `InvalidConfiguration` error listing the available renderers.

See {doc}`/reference/environment-variables` for the corresponding environment variable.

(repo-extends)=
## `extends`

```{note}
The `extends` field is reserved for a future version.
It is accepted by the schema but not yet processed by the generator.
```

The `extends` field declares that this repository builds on top of another template repository.
When implemented, it will allow organizations to:

- Inherit templates from an upstream source (such as the Plone community repository).
- Override specific templates with custom versions.
- Add new templates on top of the upstream set.

```json
{
  "extends": "gh:plone/cookieplone-templates"
}
```

## Backward compatibility

Repositories that use the legacy `cookiecutter.json` format (a flat `templates` mapping without groups or versioning) continue to work.
Cookieplone checks for `cookieplone-config.json` first, then falls back to `cookiecutter.json`.

## Full example

```json
{
  "version": "1.0",
  "title": "Plone Community Templates",
  "description": "Official Cookieplone templates for the Plone community",
  "extends": "",
  "groups": {
    "projects": {
      "title": "Projects",
      "description": "Generators that create a new Plone project",
      "templates": ["project", "classic_project"],
      "hidden": false
    },
    "add-ons": {
      "title": "Add-ons",
      "description": "Extend Plone with add-ons",
      "templates": ["backend_addon", "frontend_addon"],
      "hidden": false
    },
    "sub": {
      "title": "Sub-Templates",
      "description": "Templates used only for internal purposes",
      "templates": ["sub/cache"],
      "hidden": true
    }
  },
  "templates": {
    "project": {
      "path": "./templates/projects/monorepo",
      "title": "Volto Project",
      "description": "Create a new Plone project that uses the Volto frontend",
      "hidden": false
    },
    "classic_project": {
      "path": "./templates/projects/classic",
      "title": "Classic UI Project",
      "description": "Create a new Plone project that uses Classic UI",
      "hidden": false
    },
    "backend_addon": {
      "path": "./templates/add-ons/backend",
      "title": "Backend Add-on",
      "description": "Create a new Python package to be used with Plone",
      "hidden": false
    },
    "frontend_addon": {
      "path": "./templates/add-ons/frontend",
      "title": "Frontend Add-on",
      "description": "Create a new Node package to be used with Volto",
      "hidden": false
    },
    "sub/cache": {
      "path": "./templates/sub/cache",
      "title": "Cache settings",
      "description": "Sub-template with cache settings.",
      "hidden": true
    }
  },
  "config": {
    "versions": {
      "gha_version_checkout": "v6",
      "frontend_pnpm": "10.20.0"
    }
  }
}
```

## Related pages

- {doc}`/concepts/template-repositories`: how template repositories are structured.
- {doc}`/reference/schema-v2`: the per-template schema format.
- {doc}`/concepts/subtemplates`: how sub-templates compose.
