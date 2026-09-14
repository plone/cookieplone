---
myst:
  html_meta:
    "description": "Reference for the aurora_nick template: a Plone Aurora project that uses Nick as its backend."
    "property=og:description": "Reference for the aurora_nick template: a Plone Aurora project that uses Nick as its backend."
    "property=og:title": "Plone Aurora (alpha) using Nick as backend"
    "keywords": "Cookieplone, aurora_nick, template, Aurora, Nick, project, reference"
---

# Plone Aurora (alpha) using Nick as backend

The `aurora_nick` template creates a Plone Aurora project that uses Nick as its backend.

```console
uvx cookieplone aurora_nick
```

| | |
|---|---|
| Template ID | `aurora_nick` |
| Group | Projects |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/projects/aurora_nick` |
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
  - `Plone Aurora (alpha) using Nick as backend`
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
  - Aurora Add-on Name
  - `aurora-{{ cookiecutter.project_slug }}`
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

The template always runs these sub-templates:

| Sub-template | Generates |
|---|---|
| `sub/nick_backend` | `backend`: the Nick backend |
| `add-ons/aurora_addon` | `frontend`: the Aurora workspace and the project's Aurora add-on |
| `ci/gh_aurora_nick` | `.github`: GitHub Actions workflows |
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
│   ├── .gitignore
│   ├── .npmignore
│   ├── .pnpmfile.cjs
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── .storybook/
│   │   ├── main.js
│   │   └── preview.jsx
│   ├── .stylelintrc
│   ├── acceptance/
│   │   ├── README.md
│   │   └── tests/
│   ├── Dockerfile
│   ├── eslint.config.mjs
│   ├── Makefile
│   ├── mrs.developer.json
│   ├── package.json
│   ├── packages/
│   │   └── aurora-project-title/
│   ├── playwright-acceptance.config.ts
│   ├── pnpm-workspace.yaml
│   ├── README.md
│   └── registry.config.ts
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

Start the backend at `http://localhost:8080` and Aurora at `http://localhost:3000`, each in its own terminal:

```console
make backend-start
make frontend-start
```
