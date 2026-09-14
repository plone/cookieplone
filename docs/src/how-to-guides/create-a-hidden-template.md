---
myst:
  html_meta:
    "description": "How to hide a template or a group of templates in a Cookieplone template repository."
    "property=og:description": "How to hide a template or a group of templates in a Cookieplone template repository."
    "property=og:title": "Create a hidden template"
    "keywords": "Cookieplone, hidden template, template repository, cookieplone-config.json, groups, --all flag"
---

# Create a hidden template

A hidden template doesn't appear in Cookieplone's menu, but you can still run it by its ID.
Hide templates that a post-generation hook generates, templates that aren't ready yet, and tools for the repository's maintainers.

The examples on this page come from the example repository `docs/_examples/template-features/` in the Cookieplone source tree.

## Hide a template

In the repository's `cookieplone-config.json`, set `"hidden": true` on the template:

```json
{
  "templates": {
    "internal": {
      "path": "./templates/internal",
      "title": "Internal tool",
      "description": "A template for maintainers.",
      "hidden": true
    }
  }
}
```

A hidden template still belongs to exactly one group, like every other template.

## Hide a group

Set `"hidden": true` on a group to hide the group together with all its templates:

```json
{
  "groups": {
    "internal": {
      "title": "Internal",
      "description": "Templates for maintainers.",
      "templates": ["internal"],
      "hidden": true
    }
  }
}
```

A visible group whose templates are all hidden doesn't appear in the menu either.

The complete configuration of the example repository has a visible group and a hidden one:

```{literalinclude} ../../_examples/template-features/my-templates/cookieplone-config.json
:language: json
```

## Run a hidden template

Pass the template ID to Cookieplone:

```console
COOKIEPLONE_REPOSITORY=./my-templates uvx cookieplone internal
```

Cookieplone runs a template selected by ID whether it's hidden or not.

## Show hidden templates in the menu

Pass `--all`, or its short form `-a`:

```console
COOKIEPLONE_REPOSITORY=./my-templates uvx cookieplone --all
```

The menu then includes hidden groups and hidden templates.

## Related pages

- {doc}`/reference/cli`: the `--all` option.
- {doc}`/reference/repository-config`: the `hidden` keys of groups and templates.
- {doc}`/concepts/subtemplates`: how templates generate other templates.
- {doc}`/concepts/template-repositories`: the structure of a template repository.
