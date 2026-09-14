---
myst:
  html_meta:
    "description": "Cookieplone is your starting point for every Plone project—run one command and get a fully configured codebase."
    "property=og:description": "Cookieplone is your starting point for every Plone project—run one command and get a fully configured codebase."
    "property=og:title": "Cookieplone"
    "keywords": "Cookieplone, Plone, Cookiecutter, templates, scaffolding, project generator"
---

# Cookieplone

Your starting point for every Plone project.

Cookieplone generates Plone projects, add-ons, and documentation scaffolds from templates.
This documentation covers Cookieplone 2.0.

## Quick start

```console
uvx cookieplone
```

Cookieplone downloads the templates from [`cookieplone-templates`](https://github.com/plone/cookieplone-templates), asks you a few questions, and generates the project.

## Start here

Pick the page that matches what you came to do:

- **Install Cookieplone**—{doc}`install` covers `uvx`, `uv tool install`, and virtual environments.
- **Create a Plone project**—{doc}`tutorials/create-your-first-plone-project` walks you through your first generation.
- **Build your own template**—{doc}`tutorials/create-a-template`, then {doc}`concepts/template-repositories`.
- **Generate projects in CI**—{doc}`how-to-guides/automate-with-ci` runs Cookieplone without questions.
- **Look something up**—{doc}`reference/index` covers the command line, the file formats, and the Python API.
- **Contribute to Cookieplone**—{doc}`how-to-guides/set-up-dev-environment` sets up a development environment.
- **Something is broken**—{doc}`troubleshooting` is organized by symptom.

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} 🚀 Tutorials
:link: tutorials/index
:link-type: doc

Learn by doing.
Generate your first Plone project, or build a template repository from scratch.
````

````{grid-item-card} 🧭 How-to guides
:link: how-to-guides/index
:link-type: doc

Run Cookieplone in CI, update an existing project, use a custom template repository, and write templates with validators, computed fields, filters, and hooks.
````

````{grid-item-card} 📖 Reference
:link: reference/index
:link-type: doc

The command line, environment variables, configuration, the repository and template formats, validators, filters, and the Python API for hooks.
````

````{grid-item-card} 💡 Concepts
:link: concepts/index
:link-type: doc

How Cookieplone works: template repositories, hooks, sub-templates, validators and filters, computed defaults, and answers.
````

````{grid-item-card} 🩺 Troubleshooting
:link: troubleshooting
:link-type: doc

Symptoms, causes, and fixes for the failures you're most likely to meet.
````
`````

## What you need

| | |
|---|---|
| Python | 3.10, 3.11, 3.12, 3.13, or 3.14 |
| uv | To run Cookieplone with `uvx`, the recommended way |
| git | To use templates from a git repository, including the default one |

The official templates check for more tools, such as Node.js.
See {doc}`install` for each template's requirements, and {doc}`reference/compatibility` for supported versions.

```{toctree}
:caption: Tutorials
:maxdepth: 2
:hidden: true

install
tutorials/index
```

```{toctree}
:caption: How-to guides
:maxdepth: 2
:hidden: true

how-to-guides/index
```

```{toctree}
:caption: Reference
:maxdepth: 2
:hidden: true

reference/index
```

```{toctree}
:caption: Concepts
:maxdepth: 2
:hidden: true

concepts/index
```

```{toctree}
:caption: Appendices
:maxdepth: 2
:hidden: true

troubleshooting
glossary
genindex
```
