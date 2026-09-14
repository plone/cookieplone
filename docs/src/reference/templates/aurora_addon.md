---
myst:
  html_meta:
    "description": "Reference for the aurora_addon template: a frontend add-on package for Plone Aurora."
    "property=og:description": "Reference for the aurora_addon template: a frontend add-on package for Plone Aurora."
    "property=og:title": "Plone Aurora Frontend Add-on"
    "keywords": "Cookieplone, aurora_addon, seven_addon, template, add-on, Aurora, reference"
---

# Plone Aurora Frontend Add-on

The `aurora_addon` template creates a frontend add-on package for Plone Aurora.

```console
uvx cookieplone aurora_addon
```

| | |
|---|---|
| Template ID | `aurora_addon` |
| Group | Add-ons |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/add-ons/aurora_addon` |
| Folder generated with the default answers | `plone-aurora-add-on` |

The hidden template ID `seven_addon` points to the same folder.

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
  - `Plone Aurora Add-on`
  - —
  - —
* - `frontend_addon_name`
  - Frontend Add-on Name
  - `{{ cookiecutter.title | slugify }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `project_slug`
  - Project Slug
  - `{{ cookiecutter.title | slugify }}`
  - —
  - —
* - `description`
  - Description
  - `A new add-on for Plone Aurora.`
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
* - `aurora_version`
  - Aurora Version
  - `{{ '' | latest_aurora }}`
  - —
  - —
:::

<!-- vale on -->

% questions:end

## What your answers change

The template always runs the `ide/vscode` sub-template, which generates `.vscode` with Visual Studio Code settings.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
plone-aurora-add-on/
├── .cookieplone.json
├── .github/
│   └── workflows/
│       ├── acceptance.yml
│       ├── changelog.yml
│       ├── code.yml
│       ├── i18n.yml
│       ├── storybook.yml
│       └── unit.yml
├── .gitignore
├── .npmignore
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
├── acceptance/
│   ├── README.md
│   └── tests/
│       ├── accessibility.ts
│       ├── content.test.ts
│       ├── content.ts
│       ├── homepage.test.ts
│       ├── login.ts
│       ├── reset-fixture.ts
│       └── test.ts
├── Dockerfile
├── eslint.config.mjs
├── Makefile
├── mrs.developer.json
├── package.json
├── packages/
│   └── plone-aurora-add-on/
│       ├── .gitignore
│       ├── .release-it.json
│       ├── CHANGELOG.md
│       ├── index.ts
│       ├── locales/
│       ├── news/
│       ├── package.json
│       ├── public/
│       ├── towncrier.toml
│       ├── tsconfig.json
│       └── types.d.ts
├── playwright-acceptance.config.ts
├── pnpm-workspace.yaml
├── README.md
└── registry.config.ts
```

% tree:end

## Next steps

The generated `README.md` explains how to develop the add-on.
From the add-on folder, install it:

```console
make install
```

Start a Docker-based backend, then, in another terminal, start the frontend at `http://localhost:3000`:

```console
make backend-docker-start
make start
```
