---
myst:
  html_meta:
    "description": "Reference for the project template: requirements, questions, sub-templates, and generated files of a Plone 6 project."
    "property=og:description": "Reference for the project template: requirements, questions, sub-templates, and generated files of a Plone 6 project."
    "property=og:title": "Plone 6 Project"
    "keywords": "Cookieplone, project, template, Plone 6, Volto, Classic UI, monorepo, reference"
---

(template-project)=

# Plone 6 Project

The `project` template creates a Plone 6 project, with Volto or Classic UI.

```console
uvx cookieplone project
```

| | |
|---|---|
| Template ID | `project` |
| Group | Projects |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/projects/monorepo` |
| Folder generated with the default answers | `project-title` |

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
  - Project Title
  - `Project Title`
  - —
  - —
* - `description`
  - Project Description
  - `A new project using Plone 6.`
  - —
  - —
* - `project_slug`
  - Project Slug (Used for repository id)
  - `{{ cookiecutter.title | slugify }}`
  - —
  - —
* - `hostname`
  - Project URL (without protocol)
  - `{{ cookiecutter.project_slug }}.example.com`
  - —
  - `cookieplone.validators.hostname`
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
* - `python_package_name`
  - Python Package Name
  - `{{ cookiecutter.project_slug|replace(' ', '')|replace('-', '.') }}`
  - —
  - `cookieplone.validators.python_package_name`
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
* - `feature_headless`
  - Use Volto as frontend?
  - `true`
  - —
  - —
* - `volto_version`
  - Volto Version (asked only when `feature_headless` is `true`)
  - `{{ cookiecutter.use_prerelease_versions | latest_volto }}`
  - —
  - `cookieplone.validators.volto_version`
* - `frontend_addon_name`
  - Volto Addon Name (asked only when `feature_headless` is `true`)
  - `volto-{{ cookiecutter.python_package_name|replace('_', '-')|replace('.', '-') }}`
  - —
  - `cookieplone.validators.npm_package_name`
* - `language_code`
  - Language
  - `en`
  - `en` (English), `de` (Deutsch), `es` (Español), `pt-br` (Português (Brasil)), `nl` (Nederlands), `fi` (Suomi), `it` (Italiano), `sv` (Svenska)
  - `cookieplone.validators.language_code`
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
* - `devops_storage`
  - Which persistent storage to use in the deployment stack?
  - `relstorage`
  - `relstorage` (RelStorage with PostgreSQL (recommended)), `zeo` (ZEO with FileStorage), `filestorage` (Local FileStorage, implies a single backend)
  - —
* - `devops_cache`
  - Should we setup a caching server?
  - `true`
  - —
  - —
* - `devops_ansible`
  - Add Ansible playbooks?
  - `true`
  - —
  - —
* - `devops_gha_deploy`
  - Add GitHub Action to Deploy this project?
  - `true`
  - —
  - —
* - `initialize_documentation`
  - Would you like to add a documentation scaffold to your project?
  - `true`
  - —
  - —
:::

<!-- vale on -->

% questions:end

(template-project-actions)=

## What your answers change

The template generates parts of the project with sub-templates:

| Sub-template | Generates | When |
|---|---|---|
| `add-ons/backend` | `backend`: the Plone backend and the project's Python package | Always |
| `add-ons/frontend` | `frontend`: the Volto project and the project's Volto add-on | `feature_headless` is yes |
| `docs/starter` | `docs`: a documentation scaffold | `initialize_documentation` is yes |
| `sub/cache` | Cache settings for the project | `devops_cache` is yes |
| `sub/project_settings` | Project settings, such as the site language | Always |
| `ide/vscode` | `.vscode`: Visual Studio Code settings | Always |
| `ci/gh_project` | `.github`: GitHub Actions workflows | Always |

Then the post-generation hook:

- creates the namespace packages of `python_package_name` in `backend/src`;
- formats the backend code, and the frontend code when `feature_headless` is yes;
- removes the Ansible files from `devops` when `devops_ansible` is no;
- removes the GitHub Actions deployment files from `devops` when `devops_gha_deploy` is no;
- moves `docs/.readthedocs.yaml` to `.readthedocs.yml` when `initialize_documentation` is yes;
- initializes a git repository.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
project-title/
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
│       ├── manual_deploy.yml
│       ├── rtd-pr-preview.yml
│       └── varnish.yml
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
│   │   └── project/
│   ├── tests/
│   │   ├── conftest.py
│   │   └── setup/
│   └── version.txt
├── CHANGELOG.md
├── devops/
│   ├── .env_dist
│   ├── .env_gha
│   ├── .gitignore
│   ├── ansible.cfg
│   ├── etc/
│   │   ├── docker/
│   │   └── keys/
│   ├── inventory/
│   │   ├── group_vars/
│   │   └── hosts.yml
│   ├── Makefile
│   ├── playbooks/
│   │   └── setup.yml
│   ├── README-GHA.md
│   ├── README-GITLAB.md
│   ├── README.md
│   ├── requirements/
│   │   ├── collections.yml
│   │   ├── requirements.txt
│   │   └── roles.yml
│   ├── stacks/
│   │   └── project-title.example.com.yml
│   ├── tasks/
│   │   ├── base/
│   │   ├── handlers/
│   │   └── swarm/
│   └── varnish/
│       ├── Dockerfile
│       └── etc/
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
│   ├── LICENSE.md
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
│   │   └── volto-project-title/
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

The generated `README.md` explains how to work on the project.
From the project folder, install the project, create a Plone site, and start the backend at `http://localhost:8080`:

```console
make install
make backend-create-site
make backend-start
```

In another terminal, start the frontend at `http://localhost:3000`:

```console
make frontend-start
```

To run the project as a Docker Compose stack at `http://project-title.localhost`, run `make stack-create-site`, then `make stack-start`.
