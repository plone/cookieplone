---
myst:
  html_meta:
    "description": "Reference for the documentation_starter template: a Sphinx documentation scaffold for Plone projects."
    "property=og:description": "Reference for the documentation_starter template: a Sphinx documentation scaffold for Plone projects."
    "property=og:title": "Documentation scaffold for Plone projects"
    "keywords": "Cookieplone, documentation_starter, template, documentation, Sphinx, MyST, reference"
---

# Documentation scaffold for Plone projects

The `documentation_starter` template creates a Sphinx documentation scaffold for Plone projects.

```console
uvx cookieplone documentation_starter
```

| | |
|---|---|
| Template ID | `documentation_starter` |
| Group | Documentation |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/docs/starter` |
| Folder generated with the default answers | `collective.documentationstarter` |

`project`, `aurora_cmfplone`, `monorepo_addon`, `backend_addon`, and `frontend_addon` run this template as the `docs/starter` sub-template when you ask for documentation.

## Requirements

Before its first question, the template checks for Cookieplone 2.0.0a2 or later.

## Questions

Cookieplone asks these questions in this order.

% questions:begin

<!-- vale off -->

:::{list-table}
:header-rows: 1

* - Field
  - Question
  - Default
  - Choices
  - Validation
* - `title`
  - Title
  - `Documentation Starter`
  - —
  - —
* - `description`
  - Description
  - `A documentation starter scaffold for Plone`
  - —
  - —
* - `author`
  - Author
  - `Plone Community`
  - —
  - —
* - `email`
  - Author E-mail
  - `collective@plone.org`
  - —
  - —
* - `github_organization`
  - GitHub Organization
  - `collective`
  - —
  - —
* - `initialize_git`
  - Initialize Git Repository
  - `1`
  - `1` (Yes), `0` (No)
  - —
:::

<!-- vale on -->

% questions:end

## What your answers change

The post-generation hook formats the scaffold, and initializes a git repository when `initialize_git` is `1`.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
collective.documentationstarter/
├── .cookieplone.json
├── .gitignore
├── .readthedocs.yaml
├── .vale.ini
├── docs/
│   ├── _static/
│   │   ├── favicon.ico
│   │   └── logo.svg
│   ├── _templates/
│   │   └── 404.html
│   ├── concepts/
│   │   └── index.md
│   ├── conf.py
│   ├── glossary.md
│   ├── how-to-guides/
│   │   └── index.md
│   ├── index.md
│   ├── reference/
│   │   └── index.md
│   ├── robots.txt
│   └── tutorials/
│       └── index.md
├── LICENSE.md
├── Makefile
├── pyproject.toml
├── README.md
└── styles/
    └── config/
        └── vocabularies/
```

% tree:end

## Next steps

The generated `README.md` lists uv as a prerequisite.
From the scaffold folder, build the HTML documentation:

```console
make html
```

`make livehtml` builds the documentation and shows a live preview while you edit.
`make vale` checks spelling, grammar, and style, and `make help` lists the other targets.
