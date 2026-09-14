---
myst:
  html_meta:
    "description": "Reference for the volto_nick template: a Plone Volto project that uses Nick as its backend."
    "property=og:description": "Reference for the volto_nick template: a Plone Volto project that uses Nick as its backend."
    "property=og:title": "Plone Volto using Nick as backend"
    "keywords": "Cookieplone, volto_nick, template, Volto, Nick, project, reference"
---

# Plone Volto using Nick as backend

The `volto_nick` template creates a Plone Volto project that uses Nick as its backend.

```console
uvx cookieplone volto_nick
```

| | |
|---|---|
| Template ID | `volto_nick` |
| Group | Projects |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/projects/volto_nick` |
| Folder generated with the default answers | `project-title` |

## Requirements

Before its first question, the template checks for:

- Cookieplone 2.0.0a2 or later.
- Node.js 20, 22, 23, or 24.
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
  - Project Title
  - `Project Title`
  - —
  - —
* - `project_slug`
  - Project Slug
  - `{{ cookiecutter.title | slugify }}`
  - —
  - —
* - `description`
  - Description
  - `Plone Volto using Nick as backend.`
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
  - `{{ cookiecutter.project_slug }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `frontend_addon_name`
  - Volto Add-on Name
  - `volto-{{ cookiecutter.project_slug }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `use_prerelease_versions`
  - Should we use prerelease versions?
  - `false`
  - —
  - —
* - `volto_version`
  - Volto Version
  - `{{ cookiecutter.use_prerelease_versions | latest_volto }}`
  - —
  - `cookieplone.validators.volto_version`
:::

<!-- vale on -->

% questions:end

## What your answers change

The template always runs these sub-templates:

| Sub-template | Generates |
|---|---|
| `sub/nick_backend` | `backend`: the Nick backend |
| `add-ons/frontend` | `frontend`: the Volto project and the project's Volto add-on, configured to use the backend at `http://localhost:8080` |
| `ci/gh_volto_nick` | `.github`: GitHub Actions workflows |
| `ide/vscode` | `.vscode`: Visual Studio Code settings |

After generation, the template prints the next steps.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
project-title/
├── .cookieplone.json
├── .editorconfig
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── backend.yml
│       ├── changelog.yml
│       ├── config.yml
│       ├── frontend.yml
│       └── main.yml
├── .gitignore
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── backend/
│   ├── .gitignore
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── babel.config.json
│   ├── config.ts
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── eslint.config.ts
│   ├── knexfile.ts
│   ├── Makefile
│   ├── mrs.developer.json
│   ├── package.json
│   ├── pnpm-workspace.yaml
│   ├── README.md
│   ├── src/
│   │   ├── events/
│   │   ├── migrations/
│   │   └── profiles/
│   └── tsconfig.json
├── CHANGELOG.md
├── dependabot.yml
├── frontend/
│   ├── .eslintrc.js
│   ├── .gitignore
│   ├── .npmignore
│   ├── .npmrc
│   ├── .pnpmfile.cjs
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── .storybook/
│   │   ├── main.js
│   │   └── preview.jsx
│   ├── .stylelintrc
│   ├── cypress/
│   │   ├── .gitkeep
│   │   ├── support/
│   │   ├── tests/
│   │   └── tsconfig.json
│   ├── cypress.config.js
│   ├── Makefile
│   ├── mrs.developer.json
│   ├── package.json
│   ├── packages/
│   │   └── volto-project-title/
│   ├── pnpm-workspace.yaml
│   ├── README.md
│   └── volto.config.js
├── Makefile
├── news/
│   └── .changelog_template.jinja
├── README.md
├── repository.toml
├── towncrier.toml
└── version.txt
```

% tree:end

## Next steps

The generated `README.md` lists Node.js 24, pnpm, Make, and PostgreSQL as prerequisites.
From the project folder, install the project:

```console
make install
```

Configure the PostgreSQL connection in `backend/config.ts`, then initialize the database:

```console
make backend-migrate
make backend-seed
```

Start the backend at `http://localhost:8080` and the frontend at `http://localhost:3000`, each in its own terminal:

```console
make backend-start
make frontend-start
```
