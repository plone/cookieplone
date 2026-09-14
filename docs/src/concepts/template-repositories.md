---
myst:
  html_meta:
    "description": "An explanation of what a Cookieplone template repository is and how it is structured."
    "property=og:description": "An explanation of what a Cookieplone template repository is and how it is structured."
    "property=og:title": "Template repositories"
    "keywords": "Cookieplone, template repository, cookieplone-config.json, templates, groups, hidden, git, local path"
---

# Template repositories

A template repository is a directory, git repository, or zip archive that contains one or more Cookieplone templates.
Cookieplone reads the repository's configuration, presents its templates in a menu, and generates the one you choose.

## Repository configuration

Every template repository has a `cookieplone-config.json` file at its root.
It describes the repository, not a single template: which templates exist, where they live, and how the menu groups them.

```{literalinclude} ../../_examples/template-features/my-templates/cookieplone-config.json
:language: json
```

| Key | Required | Description |
|---|---|---|
| `version` | yes | Version of the configuration format. Must be `"1.0"`. |
| `title` | yes | Name of the repository. |
| `description` | no | One-sentence description of the repository. |
| `groups` | yes, in practice | Categories of the first menu. Every template must belong to exactly one group. |
| `templates` | yes, unless `extends` is set | Templates of the repository, by template ID. |
| `config` | no | Settings for all templates: `versions`, `renderer`, `min_version`, and `summary`. |
| `extends` | no | Another repository whose templates this one inherits. |

Each entry under `templates` has these keys:

| Key | Required | Description |
|---|---|---|
| `path` | yes | Path from the repository root to the template directory. |
| `title` | yes | Name shown in the menu. |
| `description` | yes | One-sentence description shown in the menu. |
| `hidden` | no | When `true`, the template is left out of the menu. |

Each entry under `groups` has these keys:

| Key | Required | Description |
|---|---|---|
| `title` | yes | Name shown in the menu. |
| `description` | yes | One-sentence description shown in the menu. |
| `templates` | yes | IDs of the templates in the group, at least one. |
| `hidden` | no | When `true`, the group and its templates are left out of the menu. |

See {doc}`/reference/repository-config` for every key, including `config` and `extends`.

## Directory layout

```text
my-templates/
├── cookieplone-config.json          ← repository configuration
└── templates/
    ├── features/
    │   ├── cookieplone.json         ← questions and settings of the template
    │   ├── hooks/                   ← optional hooks
    │   ├── my_validators.py         ← optional Python helpers
    │   └── {{ cookiecutter.project_slug }}/
    │       └── ...
    └── internal/
        ├── cookieplone.json
        └── {{ cookiecutter.project_slug }}/
            └── ...
```

Each template directory has its own `cookieplone.json` (see {doc}`/reference/schema-v2`), an optional `hooks/` directory, and a directory named with a Jinja2 expression that becomes the generated project.
Keep templates under `templates/`: sub-templates are addressed by their path under that directory (see {doc}`/concepts/subtemplates`).

## Supported sources

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

Set the source with the `COOKIEPLONE_REPOSITORY` environment variable.
The positional argument of `cookieplone` is a template ID inside that repository, not a repository.
Without `COOKIEPLONE_REPOSITORY`, Cookieplone uses `gh:plone/cookieplone-templates`, the official [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) repository.

A local directory can be a plain directory or a git repository.
A git repository needs at least one commit.

## Hidden templates

A template or group marked `"hidden": true` is left out of the menu.
Pass `--all` (short: `-a`) to include hidden groups and templates, or pass a template ID to run a hidden template directly.

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

1. Resolves the repository source, and clones or unpacks it when it's remote.
2. Reads `cookieplone-config.json`, merging the upstream configuration when `extends` is set.
3. Validates the configuration, and checks `config.min_version` against the running Cookieplone.
4. Selects the template passed on the command line, hidden or not.
   Without one, it shows the groups, then the templates of the chosen group, in the order the configuration lists them.
   Hidden groups and templates are left out unless you pass `--all`.

## Related pages

- {doc}`/concepts/subtemplates`: how templates generate other templates.
- {doc}`/how-to-guides/create-a-hidden-template`: hide a template or a group.
- {doc}`/how-to-guides/extend-an-upstream-template-repository`: build a downstream repository on top of an upstream one.
- {doc}`/how-to-guides/use-a-custom-template-repository`: use a repository other than the default.
- {doc}`/reference/repository-config`: every key of `cookieplone-config.json`.
- {doc}`/reference/schema-v2`: the per-template `cookieplone.json` schema.
- {doc}`/reference/environment-variables`: `COOKIEPLONE_REPOSITORY` and `COOKIEPLONE_REPOSITORY_TAG`.
