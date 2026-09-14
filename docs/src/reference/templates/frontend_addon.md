---
myst:
  html_meta:
    "description": "Reference for the frontend_addon template: a Volto add-on package for the Plone 6 frontend."
    "property=og:description": "Reference for the frontend_addon template: a Volto add-on package for the Plone 6 frontend."
    "property=og:title": "Plone 6 Frontend Add-on"
    "keywords": "Cookieplone, frontend_addon, template, add-on, Volto, Node.js, reference"
---

# Plone 6 Frontend Add-on

The `frontend_addon` template creates a Volto add-on package for the Plone 6 frontend.

```console
uvx cookieplone frontend_addon
```

| | |
|---|---|
| Template ID | `frontend_addon` |
| Group | Add-ons |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/add-ons/frontend` |
| Folder generated with the default answers | `volto-add-on` |

## Requirements

Before its first question, the template checks for:

- Node.js 18, 19, 20, 21, 22, or 24.
- git.

## Questions

Cookieplone asks these questions in this order.
A default in `{{ }}` is computed from earlier answers.

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
  - Add-on Title
  - `Volto Add-on`
  - —
  - —
* - `frontend_addon_name`
  - Frontend Add-on Name
  - `{{ cookiecutter.title | slugify }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `description`
  - Description
  - `A new add-on for Volto`
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
  - `email` format
* - `github_organization`
  - GitHub Username or Organization
  - `collective`
  - —
  - —
* - `npm_package_name`
  - NPM Package Name
  - `{{ cookiecutter.frontend_addon_name }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `use_prerelease_versions`
  - Should we use prerelease versions?
  - `{{ 'No' | use_prerelease_versions }}`
  - `Yes` (Yes), `No` (No)
  - —
* - `volto_version`
  - Volto Version
  - `{{ cookiecutter.use_prerelease_versions | latest_volto }}`
  - —
  - `cookieplone.validators.volto_version`
* - `initialize_ci`
  - Add CI configuration?
  - `true`
  - —
  - —
* - `initialize_documentation`
  - Add documentation scaffold?
  - `true`
  - —
  - —
:::

<!-- vale on -->

% questions:end

## What your answers change

The post-generation hook keeps the test configuration that matches `volto_version`: Vitest for Volto 19 or later, Jest for earlier versions.
For Volto versions earlier than 19, it also removes `.pnpmfile.cjs`.

The template runs these sub-templates:

| Sub-template | Generates | When |
|---|---|---|
| `docs/starter` | `docs`: a documentation scaffold | `initialize_documentation` is yes |
| `ide/vscode` | `.vscode`: Visual Studio Code settings | `initialize_ci` is yes |
| `ci/gh_frontend_addon` | `.github`: GitHub Actions workflows | `initialize_ci` is yes |

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
volto-add-on/
├── .cookieplone.json
├── .eslintrc.js
├── .github/
│   ├── dependabot.yml
│   ├── instructions/
│   │   ├── docs.instructions.md
│   │   ├── general/
│   │   └── volto.instructions.md
│   └── workflows/
│       ├── changelog.yml
│       ├── config.yml
│       └── main.yml
├── .gitignore
├── .npmignore
├── .npmrc
├── .pnpmfile.cjs
├── .prettierignore
├── .prettierrc
├── .storybook/
│   ├── main.js
│   └── preview.jsx
├── .stylelintrc
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── cypress/
│   ├── .gitkeep
│   ├── support/
│   │   ├── commands.js
│   │   ├── e2e.js
│   │   └── index.ts
│   ├── tests/
│   │   ├── .gitkeep
│   │   └── example.cy.js
│   └── tsconfig.json
├── cypress.config.js
├── docs/
│   ├── .gitignore
│   ├── .readthedocs.yaml
│   ├── .vale.ini
│   ├── docs/
│   │   ├── _static/
│   │   ├── _templates/
│   │   ├── concepts/
│   │   ├── conf.py
│   │   ├── glossary.md
│   │   ├── how-to-guides/
│   │   ├── index.md
│   │   ├── reference/
│   │   ├── robots.txt
│   │   └── tutorials/
│   ├── LICENSE.md
│   ├── Makefile
│   ├── pyproject.toml
│   ├── README.md
│   └── styles/
│       └── config/
├── Makefile
├── mrs.developer.json
├── package.json
├── packages/
│   └── volto-add-on/
│       ├── .gitignore
│       ├── .release-it.json
│       ├── babel.config.js
│       ├── CHANGELOG.md
│       ├── locales/
│       ├── news/
│       ├── package.json
│       ├── public/
│       ├── src/
│       ├── towncrier.toml
│       ├── tsconfig.json
│       └── vitest.config.mjs
├── pnpm-workspace.yaml
├── README.md
└── volto.config.js
```

% tree:end

## Next steps

The generated `README.md` lists nvm, Node.js 24 with pnpm, Make, and git as prerequisites, and Docker as optional.
From the add-on folder, install the add-on:

```console
make install
```

Start a Docker-based backend, then, in another terminal, start Volto at `http://localhost:3000`:

```console
make backend-docker-start
make start
```
