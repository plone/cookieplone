---
myst:
  html_meta:
    "description": "Reference for the official Cookieplone templates: requirements, questions, and generated files."
    "property=og:description": "Reference for the official Cookieplone templates: requirements, questions, and generated files."
    "property=og:title": "Official templates"
    "keywords": "Cookieplone, cookieplone-templates, templates, project, add-on, documentation, questions, reference"
---

# Official templates

[`cookieplone-templates`](https://github.com/plone/cookieplone-templates) is the template repository Cookieplone uses by default.
These pages describe its visible templates: what each one checks before it starts, the questions it asks, what your answers change, and the files it generates.

| Template ID | Title | Group |
|---|---|---|
| [`project`](project.md) | Plone 6 Project | Projects |
| [`aurora_cmfplone`](aurora_cmfplone.md) | Plone Aurora (alpha) with Plone backend | Projects |
| [`volto_nick`](volto_nick.md) | Plone Volto using Nick as backend | Projects |
| [`aurora_nick`](aurora_nick.md) | Plone Aurora (alpha) using Nick as backend | Projects |
| [`aurora_nick_embedded`](aurora_nick_embedded.md) | Plone Aurora (alpha) using Nick as an embedded library (experimental) | Projects |
| [`monorepo_addon`](monorepo_addon.md) | Plone 6 Add-on (Frontend and Backend) | Add-ons |
| [`backend_addon`](backend_addon.md) | Plone 6 Backend Add-on (Python) | Add-ons |
| [`frontend_addon`](frontend_addon.md) | Plone 6 Frontend Add-on | Add-ons |
| [`aurora_addon`](aurora_addon.md) | Plone Aurora Frontend Add-on | Add-ons |
| [`documentation_starter`](documentation_starter.md) | Documentation scaffold for Plone projects | Documentation |

## Run a template

Choose a template from the menu that `uvx cookieplone` shows, or pass its ID:

```console
uvx cookieplone project
```

The repository also has hidden templates, such as the sub-templates and continuous integration configurations that the visible templates use.
`cookieplone --all` adds them to the menu.

## Defaults from your git configuration

Cookieplone pre-fills the `author` and `email` questions with `user.name` and `user.email` from your git configuration.
The `default_context` of your configuration file takes precedence.
See {doc}`/reference/configuration`.

## How these pages are built

The questions table and the file tree of each page come from a generation of the template with `--no-input`, which uses the default answers.
`docs/_checks/template_pages.py` in the Cookieplone repository checks them against that generation.

```{toctree}
:hidden: true
:maxdepth: 1

project
aurora_cmfplone
volto_nick
aurora_nick
aurora_nick_embedded
monorepo_addon
backend_addon
frontend_addon
aurora_addon
documentation_starter
```
