---
myst:
  html_meta:
    "description": "An explanation of what a Cookieplone template repository is and how it is structured."
    "property=og:description": "An explanation of what a Cookieplone template repository is and how it is structured."
    "property=og:title": "Template repositories"
    "keywords": "Cookieplone, template repository, cookiecutter.json, templates, hidden, git, local path"
---

# Template repositories

A template repository is a git repository (or local directory) that contains one or more Cookieplone templates.
Cookieplone clones or copies the repository, reads its manifest, and presents the available templates to you.

## Repository manifest

Every template repository must contain a `cookiecutter.json` file at its root.
This root manifest is different from the per-template schema files—it describes the repository, not a single template.

```json
{
  "templates": {
    "project": {
      "path": "./templates/project",
      "title": "A Plone project",
      "description": "Full Plone project with backend and frontend."
    },
    "addon": {
      "path": "./templates/addon",
      "title": "A Plone add-on",
      "description": "Minimal installable Plone add-on."
    }
  }
}
```

Each entry under `templates` has:

| Key | Required | Description |
|---|---|---|
| `path` | yes | Relative path from the repository root to the template directory. |
| `title` | yes | Short name shown in the selection menu. |
| `description` | yes | One-sentence description shown under the title. |
| `hidden` | no | When `true`, the template is omitted from the default menu. |

## Directory layout

```
my-templates/
├── cookiecutter.json          # repository manifest
└── templates/
    ├── project/               # a full template
    │   ├── cookieplone.json   # template schema (v2)
    │   ├── hooks/
    │   │   └── pre_prompt.py
    │   └── {{cookiecutter.project_slug}}/
    │       └── ...
    └── addon/
        ├── cookieplone.json
        └── {{cookiecutter.python_package_name}}/
            └── ...
```

Each sub-directory listed in the manifest is an independent Cookiecutter template with its own schema file and optional `hooks/` directory.

## Supported source types

Cookieplone accepts any of these repository sources:

| Source | Example |
|---|---|
| Git URL (HTTPS) | `https://github.com/plone/cookieplone-templates.git` |
| Git URL (SSH) | `git@github.com:plone/cookieplone-templates.git` |
| GitHub abbreviation | `gh:plone/cookieplone-templates` |
| GitLab abbreviation | `gl:myorg/my-templates` |
| Bitbucket abbreviation | `bb:myorg/my-templates` |
| Local directory | `/home/user/my-templates` |
| Zip archive (URL or path) | `https://example.com/templates.zip` |

Set the source via `COOKIEPLONE_REPOSITORY` or the positional `template` argument combined with a repository override.

## Hidden templates

A template marked `"hidden": true` is not shown in the default selection menu.
Pass `--all` (short: `-a`) to include hidden templates in the menu.

Hidden templates are useful for:

- Sub-templates called programmatically from a post-generation hook.
- Experimental or work-in-progress templates.
- Internal maintenance templates.

See {doc}`/how-to-guides/create-a-hidden-template` for an example.

## Inheritance via `extends`

A repository can declare an `extends` field in its `cookieplone-config.json` to **inherit templates from another repository** instead of forking it.
The upstream repository is cloned at runtime, its configuration is merged underneath the downstream, and the combined template list is shown to the user.

The merge follows **downstream-wins** semantics:

- A template `id` that appears in both repositories resolves to the downstream definition.
- A template `id` that only appears upstream is visible as if it were local.
- A template `id` that only appears downstream is added on top.
- A downstream can hide an upstream template by redeclaring it with `"hidden": true`.

`config.versions` is shallow-merged per key, `config.renderer` follows downstream-first-with-upstream-fallback, and `config.min_version` is strictest-wins via PEP 440 ordering.

Chains are supported: `A` may extend `B`, which may extend `C`.
The resolution is bounded by a depth limit, and cycles are detected.

For the complete merge-rules table and error semantics, see {ref}`repo-extends`.
For a worked walkthrough, see {doc}`/how-to-guides/extend-an-upstream-template-repository`.

```{note}
Group-level merging is currently replace-or-nothing: a downstream that redeclares a group inherits no entries from the upstream group. An opt-in append mode is tracked in [issue #185](https://github.com/plone/cookieplone/issues/185).
```

## Template discovery

When Cookieplone starts, it:

1. Resolves and clones the repository.
2. Reads the root `cookiecutter.json`.
3. Builds the list of templates from the `templates` key.
4. Filters out hidden templates unless `--all` is passed.
5. Presents the remaining templates in the order they appear in the manifest.

## Related pages

- {doc}`/concepts/subtemplates`: how multiple templates within one repository compose.
- {doc}`/how-to-guides/create-a-hidden-template`: mark a template as hidden.
- {doc}`/how-to-guides/extend-an-upstream-template-repository`: build a downstream repository on top of an upstream one.
- {doc}`/how-to-guides/use-a-custom-template-repository`: use a repository other than the default.
- {doc}`/reference/schema-v2`: the per-template `cookieplone.json` schema.
- {doc}`/reference/environment-variables`: `COOKIEPLONE_REPOSITORY` and `COOKIEPLONE_REPOSITORY_TAG`.
