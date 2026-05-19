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
| `extends` | string \| object | no | Repository to inherit templates from (see {ref}`repo-extends`). |
| `groups` | object | no | Template groups for the selection menu (see {ref}`repo-groups`). |
| `templates` | object | yes¹ | Template definitions (see {ref}`repo-templates`). |

¹ `templates` is optional when `extends` is set—see {ref}`repo-extends`.
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
    "min_version": "2.0.0a2",
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

### `config.min_version`

Declares the minimum Cookieplone version required by the templates in this repository.
The value must be a valid [PEP 440](https://peps.python.org/pep-0440/) version string, including pre-release versions such as `2.0.0a1`.

```json
{
  "config": {
    "min_version": "2.0.0a2"
  }
}
```

When present, Cookieplone compares the installed version against this value before any generation begins.
If the installed version is older, generation stops with an actionable error message:

```text
This template requires cookieplone >= 2.0.0a2, but you have 1.3.0 installed.
Please upgrade:  uvx --no-cache cookieplone@2.0.0a2
```

When the key is absent or empty, no version check is performed (backwards compatible with existing repositories).

(repo-extends)=
## `extends`

The `extends` field declares that this repository builds on top of another template repository.
It lets organizations keep a minimal repository with only their local templates and overrides while transparently consuming an upstream, mirroring how `extends` works in GitLab CI and similar inheritance systems.

A downstream repository can:

- **Inherit** every template and group from upstream by default.
- **Override** a specific template by redeclaring it under the same `id`.
- **Add** brand-new templates on top of the upstream set.
- **Hide** an upstream template by redeclaring it with `"hidden": true`.

When `extends` is set, the `templates` field is optional—a "pure-extension" downstream that only inherits is valid.

### Forms

`extends` accepts either a string or an object:

```json
{
  "extends": "gh:plone/cookieplone-templates"
}
```

```json
{
  "extends": {
    "url": "gh:plone/cookieplone-templates",
    "tag": "2.1.0"
  }
}
```

The object form pins the upstream to a specific tag or branch for reproducibility.
The string form uses the upstream default branch.

### Merge rules

When a downstream declares `extends`, Cookieplone clones the upstream and merges its config underneath the downstream with the following rules.

| Field | Rule |
|---|---|
| `version` | Downstream wins (the merged result must satisfy the downstream schema version). |
| `title` / `description` | Downstream wins. |
| `extends` | Stripped from the merged result. |
| `templates` | Keyed union; a downstream entry merges per-field with the upstream entry of the same `id`. Downstream wins per field; fields the downstream omits inherit from upstream. When the downstream entry supplies `path`, its template directory is overlaid on top of upstream's at render time. |
| `groups` | Keyed union; a downstream group entry replaces the upstream entry with the same `id`. The `templates` list inside a group is **replaced** wholesale, not merged. |
| `config.versions` | Shallow merge, downstream wins per key. |
| `config.renderer` | Downstream wins if set; otherwise falls back to upstream. |
| `config.min_version` | Stricter wins: `max(upstream.min_version, downstream.min_version)` using PEP 440 ordering. |

```{note}
Group-level merging is currently **replace-or-nothing**: a downstream that redeclares a group inherits no entries from the upstream group. To add a single template to an upstream group, the downstream must re-list every upstream template ID in that group.

An opt-in append mode is tracked in [issue #185](https://github.com/plone/cookieplone/issues/185).
```

### Partial redeclares

When a downstream redeclares a template that exists upstream, the entry is merged per field. The downstream may declare just the fields it wants to change:

```json
"templates": {
  "project": {"hidden": true}
}
```

This *hides* the upstream `project` template without supplying a local `path` / `title` / `description`: the missing fields are filled from upstream after merge.

When the downstream supplies a `path`, the downstream entry's directory is **overlaid on top of upstream's** at render time. The generator walks the upstream template first, then copies the downstream template directory on top, so a downstream may override individual files (for example `README.md`) while inheriting the upstream `cookieplone.json`, hooks, and everything else:

```json
"templates": {
  "project": {
    "path": "./templates/project",
    "title": "Override of upstream"
  }
}
```

```
templates/project/
└── {{ cookiecutter.__folder_name }}/
    └── README.md       # overrides upstream's README
```

The overlay is materialised in a temporary directory and cleaned up after the run.

### Transitive inheritance

`extends` follows chains. If `A` extends `B` and `B` extends `C`, then `A` resolves to `C ∪ B ∪ A` with each downstream layer winning over the layers below it.

To prevent runaway resolution, the chain is bounded by `MAX_EXTENDS_DEPTH = 5`.
A circular chain (`A → B → A`) is detected and reported with the full cycle.

### Errors

| Failure | Behaviour |
|---|---|
| Upstream URL unreachable | `RepositoryException` naming the URL and the underlying clone error. |
| Schema validation fails on a loaded link | `RuntimeError` listing the validation errors. |
| Cycle detected | `InvalidConfiguration` with the full cycle, for example `A → B → A`. |
| Depth limit exceeded | `InvalidConfiguration` with the chain so far. |
| Cross-referential check fails on the merged result | `RuntimeError` explaining which template/group declaration is at fault. |

See {ref}`extend-an-upstream-template-repository` for a worked walkthrough.

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
    "min_version": "2.0.0a2",
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
