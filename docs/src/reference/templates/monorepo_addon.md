---
myst:
  html_meta:
    "description": "Reference for the monorepo_addon template: a Plone 6 add-on with a Python backend and a Volto frontend."
    "property=og:description": "Reference for the monorepo_addon template: a Plone 6 add-on with a Python backend and a Volto frontend."
    "property=og:title": "Plone 6 Add-on (Frontend and Backend)"
    "keywords": "Cookieplone, monorepo_addon, template, add-on, backend, frontend, Volto, reference"
---

# Plone 6 Add-on (Frontend and Backend)

The `monorepo_addon` template creates a codebase for a Plone 6 add-on that has both a Python backend and a Volto frontend.

```console
uvx cookieplone monorepo_addon
```

| | |
|---|---|
| Template ID | `monorepo_addon` |
| Group | Add-ons |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/add-ons/monorepo` |
| Folder generated with the default answers | `collective-addon` |

## Requirements

Before its first question, the template checks for:

- Cookieplone 2.0.0a2 or later.
- uv.
- Node.js 20, 22, or 24.
- git.
- Docker 26 or later.
  Docker is optional: when it's missing, the check shows a warning.

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
  - `Collective Addon`
  - —
  - —
* - `description`
  - Description of the add-on
  - `A new add-on for Plone that includes both backend and Volto frontend`
  - —
  - —
* - `project_slug`
  - Slug (Used for repository id)
  - `{{ cookiecutter.title | slugify }}`
  - —
  - —
* - `author`
  - Author
  - `Plone Foundation`
  - —
  - —
* - `email`
  - Author E-mail
  - `collective@plone.org`
  - —
  - `email` format
* - `use_prerelease_versions`
  - Should we use prerelease versions?
  - `false`
  - —
  - —
* - `plone_version`
  - Plone Version
  - `{{ cookiecutter.use_prerelease_versions | latest_plone }}`
  - —
  - `cookieplone.validators.plone_version`
* - `volto_version`
  - Volto Version
  - `{{ cookiecutter.use_prerelease_versions | latest_volto }}`
  - —
  - `cookieplone.validators.volto_version`
* - `python_package_name`
  - Python Package Name
  - `{{ cookiecutter.project_slug|replace(' ', '')|replace('-', '.') }}`
  - —
  - `cookieplone.validators.python_package_name`
* - `npm_package_name`
  - Volto Addon Name
  - `volto-{{ cookiecutter.python_package_name|replace('_', '-')|replace('.', '-') }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `github_organization`
  - GitHub or GitLab username or organization slug from URL
  - `collective`
  - —
  - —
* - `container_registry`
  - Container Registry
  - `github`
  - `github` (GitHub Container Registry), `docker_hub` (Docker Hub), `gitlab` (GitLab)
  - —
* - `initialize_documentation`
  - Would you like to add a documentation scaffold to your project?
  - `true`
  - —
  - —
:::

<!-- vale on -->

% questions:end

## What your answers change

The template generates parts of the codebase with sub-templates:

| Sub-template | Generates | When |
|---|---|---|
| `add-ons/backend` | `backend`: the add-on's Python package | Always |
| `add-ons/frontend` | `frontend`: the add-on's Volto package | Always |
| `docs/starter` | `docs`: a documentation scaffold | `initialize_documentation` is yes |
| `sub/addon_settings` | Add-on settings | Always |
| `ide/vscode` | `.vscode`: Visual Studio Code settings | Always |
| `ci/gh_monorepo_addon` | `.github`: GitHub Actions workflows | Always |

Then the post-generation hook:

- creates the namespace packages of `python_package_name` in `backend/src`;
- formats the backend code;
- when `initialize_documentation` is yes, moves `docs/.readthedocs.yaml` to `.readthedocs.yml` and removes `docs/LICENSE.md`;
- initializes a git repository.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
collective-addon/
├── .cookieplone.json
├── .editorconfig
├── .github/
│   ├── dependabot.yml
│   ├── instructions/
│   │   ├── docs.instructions.md
│   │   ├── general/
│   │   └── volto.instructions.md
│   └── workflows/
│       ├── backend.yml
│       ├── changelog.yml
│       ├── config.yml
│       ├── docs.yml
│       ├── frontend.yml
│       ├── main.yml
│       └── rtd-pr-preview.yml
├── .gitignore
├── .readthedocs.yml
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── backend/
│   ├── .dockerignore
│   ├── .editorconfig
│   ├── .flake8
│   ├── .gitignore
│   ├── bobtemplate.cfg
│   ├── CHANGELOG.md
│   ├── CONTRIBUTORS.md
│   ├── Dockerfile
│   ├── Dockerfile.acceptance
│   ├── instance.yaml
│   ├── LICENSE.GPL
│   ├── LICENSE.md
│   ├── Makefile
│   ├── mx.ini
│   ├── news/
│   │   ├── .changelog_template.jinja
│   │   └── .gitkeep
│   ├── pyproject.toml
│   ├── README.md
│   ├── scripts/
│   │   └── create_site.py
│   ├── src/
│   │   └── collective/
│   ├── tests/
│   │   ├── conftest.py
│   │   └── setup/
│   └── version.txt
├── CHANGELOG.md
├── docker-compose.yml
├── docs/
│   ├── .gitignore
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
│   ├── Makefile
│   ├── pyproject.toml
│   ├── README.md
│   └── styles/
│       └── config/
├── frontend/
│   ├── .dockerignore
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
│   ├── Dockerfile
│   ├── Makefile
│   ├── mrs.developer.json
│   ├── package.json
│   ├── packages/
│   │   └── volto-collective-addon/
│   ├── pnpm-workspace.yaml
│   ├── README.md
│   └── volto.config.js
├── Makefile
├── news/
│   ├── .changelog_template.jinja
│   └── .gitkeep
├── README.md
├── repository.toml
├── towncrier.toml
└── version.txt
```

% tree:end

## Next steps

The generated `README.md` explains how to work on the add-on.
From the add-on folder, install it, create a Plone site, and start the backend at `http://localhost:8080`:

```console
make install
make backend-create-site
make backend-start
```

In another terminal, start the frontend at `http://localhost:3000`:

```console
make frontend-start
```

To run the add-on in a Docker Compose stack at `http://collective-addon.localhost`, run `make stack-create-site`, then `make stack-start`.
