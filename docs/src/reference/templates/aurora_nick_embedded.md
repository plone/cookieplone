---
myst:
  html_meta:
    "description": "Reference for the aurora_nick_embedded template: a Plone Aurora project that embeds Nick as a library."
    "property=og:description": "Reference for the aurora_nick_embedded template: a Plone Aurora project that embeds Nick as a library."
    "property=og:title": "Plone Aurora (alpha) using Nick as an embedded library (experimental)"
    "keywords": "Cookieplone, aurora_nick_embedded, template, Aurora, Nick, experimental, reference"
---

# Plone Aurora (alpha) using Nick as an embedded library (experimental)

The `aurora_nick_embedded` template creates a Plone Aurora project that embeds Nick as a library.
The template is experimental.

```console
uvx cookieplone aurora_nick_embedded
```

| | |
|---|---|
| Template ID | `aurora_nick_embedded` |
| Group | Projects |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/projects/aurora_nick_embedded` |
| Folder generated with the default answers | `project-title` |

## Requirements

Before its first question, the template checks for:

- Cookieplone 2.0.0a2 or later.
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
  - Project Title
  - `Project Title`
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
  - `Plone Aurora using Nick as an embedded library.`
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

The template always runs these sub-templates:

| Sub-template | Generates |
|---|---|
| `add-ons/aurora_addon` | The Aurora workspace and add-on, in the project folder itself; the post-generation hook then adds Nick to them |
| `ide/vscode` | `.vscode`: Visual Studio Code settings |

After generation, the template prints the next steps.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
project-title/
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
│       ├── basic.test.ts
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
│   ├── project-title/
│   │   ├── .gitignore
│   │   ├── .release-it.json
│   │   ├── CHANGELOG.md
│   │   ├── config/
│   │   ├── index.ts
│   │   ├── locales/
│   │   ├── news/
│   │   ├── package.json
│   │   ├── public/
│   │   ├── towncrier.toml
│   │   ├── tsconfig.json
│   │   ├── types.d.ts
│   │   └── vite.extend.ts
│   └── project-title-nick/
│       ├── package.json
│       └── profiles/
├── playwright-acceptance.config.ts
├── pnpm-workspace.yaml
├── README.md
└── registry.config.ts
```

% tree:end

## Next steps

The generated `README.md` lists Node.js, Make, and Docker as prerequisites, and asks you to enable Corepack:

```console
npm install --global corepack@latest
corepack enable
```

From the project folder, install the project:

```console
make install
```

Start the backend, then, in another terminal, the frontend:

```console
make backend-docker-start
make start
```
