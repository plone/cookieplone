---
myst:
  html_meta:
    "description": "How to mark a template as hidden in a Cookieplone template repository."
    "property=og:description": "How to mark a template as hidden in a Cookieplone template repository."
    "property=og:title": "Create a hidden template"
    "keywords": "Cookieplone, hidden template, template repository, cookiecutter.json, --all flag"
---

# Create a hidden template

Some templates in a repository are intended for internal or advanced use, not for general discovery.
Mark them as `hidden` in the root `cookiecutter.json` to exclude them from the default template list.

## Mark a template as hidden

In the root `cookiecutter.json`, add `"hidden": true` to a template entry:

```json
{
  "templates": {
    "project": {
      "path": "./templates/project",
      "title": "A Plone project",
      "description": "Full Plone project with backend and frontend."
    },
    "cache-config": {
      "path": "./templates/sub/cache",
      "title": "Cache configuration sub-template",
      "description": "Adds cache configuration to an existing project.",
      "hidden": true
    }
  }
}
```

When a user runs `cookieplone`, the `cache-config` template does not appear in the menu.

## Show hidden templates

To list and select hidden templates, pass `--all` (short: `-a`):

```console
cookieplone --all
```

The full menu, including hidden templates, appears.

## Common use cases for hidden templates

- **Sub-templates** that are called programmatically from a post-generation hook, not directly by the user.
- **Experimental or in-progress** templates that are not ready for general use.
- **Internal maintenance** templates used only by the template repository maintainers.

## Related pages

- {doc}`/reference/cli`: `--all` flag.
- {doc}`/concepts/subtemplates`: how sub-templates work and when to use them.
- {doc}`/concepts/template-repositories`: the full template repository structure.
