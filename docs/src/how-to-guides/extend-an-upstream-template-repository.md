---
myst:
  html_meta:
    "description": "How to extend an upstream Cookieplone template repository instead of forking it."
    "property=og:description": "How to extend an upstream Cookieplone template repository instead of forking it."
    "property=og:title": "Extend an upstream template repository"
    "keywords": "Cookieplone, extends, template repository, inheritance, downstream, upstream"
---

(extend-an-upstream-template-repository)=

# Extend an upstream template repository

If your organization only needs to add one or two templates on top of the official `plone/cookieplone-templates` repository, you don't need to fork it.

Declare `extends` in your `cookieplone-config.json` and Cookieplone will resolve the upstream at runtime, merging your local overrides on top.

This guide walks through a small downstream repository that:

- **Inherits** everything from `plone/cookieplone-templates`.
- **Overrides** one upstream template with a local variant.
- **Adds** a brand-new in-house template.
- **Hides** an upstream template it does not want to expose.

## Prerequisites

- A `cookieplone-config.json` file at the root of your downstream template repository.
- Read access to the upstream repository (a public GitHub repository, a private GitHub repository with a credential, or a local checkout).

## Minimal extension

The simplest form: inherit everything, add nothing.

```json
{
  "version": "1.0",
  "title": "My Org Templates",
  "description": "In-house templates extending the Plone community set",
  "extends": "gh:plone/cookieplone-templates"
}
```

Note that `templates` is **omitted** entirely.
When `extends` is set, the field is optional.
Running Cookieplone against this repository offers the full upstream menu.

## Pin the upstream to a tag

For reproducibility, use the object form of `extends` to pin a tag or branch:

```json
{
  "version": "1.0",
  "title": "My Org Templates",
  "extends": {
    "url": "gh:plone/cookieplone-templates",
    "tag": "2.1.0"
  }
}
```

## Override, add, and hide

A realistic downstream config combines all four operations:

```json
{
  "version": "1.0",
  "title": "My Org Templates",
  "description": "In-house templates extending the Plone community set",
  "extends": "gh:plone/cookieplone-templates",
  "groups": {
    "internal": {
      "title": "Internal",
      "description": "Templates used inside My Org only",
      "templates": ["my_org/api_service"],
      "hidden": false
    }
  },
  "templates": {
    "project": {
      "path": "./templates/my_org/project",
      "title": "My Org Plone Project",
      "description": "Plone project pre-wired for our infra",
      "hidden": false
    },
    "my_org/api_service": {
      "path": "./templates/my_org/api_service",
      "title": "Internal API service",
      "description": "FastAPI service consuming plone.restapi",
      "hidden": false
    },
    "frontend_addon": {
      "path": "./templates/dummy",
      "title": "Frontend add-on",
      "description": "Hidden in this downstream",
      "hidden": true
    }
  }
}
```

What each block does:

1. **Override**: `project` reuses the upstream `id` but points at a local path with a custom title and description.
2. **Add**: `my_org/api_service` is a brand-new template not present in the upstream, listed in a new `internal` group.
3. **Hide**: `frontend_addon` is redeclared with `"hidden": true`, so it disappears from the default menu while remaining available via `cookieplone --all frontend_addon`.

The `dummy` path on a hidden redeclaration is never traversed; Cookieplone only loads template files for the entry the user actually picks.

## How the merge works

When a user runs Cookieplone against the preceding downstream, the resolver:

1. Loads your downstream config.
2. Clones the upstream named by `extends` and loads its config.
3. Merges the two with **downstream-wins** semantics (full rules in {ref}`repo-extends`).
4. Validates the merged result against the schema, including cross-referential checks (every template in a group must exist, no template in two groups).
5. Lists the merged menu to the user.

The upstream clone lives in a temporary directory for the duration of the run and is cleaned up afterwards.

## Versions and renderer

`config.versions`, `config.renderer`, and `config.min_version` also follow the merge rules:

```json
{
  "version": "1.0",
  "title": "My Org Templates",
  "extends": "gh:plone/cookieplone-templates",
  "config": {
    "versions": { "node": "22" },
    "renderer": "stdlib"
  }
}
```

`config.versions` is **shallow-merged**, so `node: "22"` overrides the upstream `node` pin while every other upstream key is inherited.
`config.renderer` is downstream-wins.
`config.min_version` is strictest-wins: if upstream requires `>=2.0` and downstream requires `>=2.1`, the merged value is `2.1`.

## Transitive chains

`extends` follows chains: a downstream may extend another downstream that itself extends upstream.
Cookieplone resolves the whole chain in one run, capped at `MAX_EXTENDS_DEPTH = 5`.
A circular chain (`A → B → A`) is detected and Cookieplone reports the full cycle.

## Limitations

```{note}
Group-level merging is currently replace-or-nothing.
To add a single template to an upstream group, you must re-list every upstream template ID in that group, and a future upstream addition to the same group will not flow through automatically.

Tracking this as an opt-in append mode in [issue #185](https://github.com/plone/cookieplone/issues/185).
```

## See also

- {ref}`repo-extends`: full reference for the `extends` field and merge rules.
- [Template repositories](../concepts/template-repositories.md): concept page covering repository layout and inheritance.
- [Use a custom template repository](use-a-custom-template-repository.md): selecting any repository (with or without `extends`) at the CLI.
