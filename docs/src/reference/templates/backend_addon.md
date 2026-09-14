---
myst:
  html_meta:
    "description": "Reference for the backend_addon template: a Python add-on package for the Plone 6 backend."
    "property=og:description": "Reference for the backend_addon template: a Python add-on package for the Plone 6 backend."
    "property=og:title": "Plone 6 Backend Add-on (Python)"
    "keywords": "Cookieplone, backend_addon, template, add-on, Python, Plone backend, reference"
---

# Plone 6 Backend Add-on (Python)

The `backend_addon` template creates a Python add-on package for the Plone 6 backend.

```console
uvx cookieplone backend_addon
```

| | |
|---|---|
| Template ID | `backend_addon` |
| Group | Add-ons |
| Folder in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) | `templates/add-ons/backend` |
| Folder generated with the default answers | `collective.addon` |

## Requirements

Before its first question, the template checks for:

- Cookieplone 2.0.0a2 or later.
- uv.
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
  - Addon Title
  - `Addon`
  - —
  - —
* - `description`
  - Description
  - `A new addon for Plone`
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
* - `use_prerelease_versions`
  - Should we use prerelease versions?
  - `{{ 'No' | use_prerelease_versions }}`
  - `Yes` (Yes), `No` (No)
  - —
* - `plone_version`
  - Plone Version
  - `{{ cookiecutter.use_prerelease_versions | latest_plone }}`
  - —
  - `cookieplone.validators.plone_version`
* - `python_package_name`
  - Python Package Name
  - `{{ cookiecutter.github_organization|lower }}.{{ cookiecutter.title|replace(' ', '')|replace('-', '_')|replace('.', '')|lower }}`
  - —
  - `cookieplone.validators.python_package_name`
* - `feature_headless`
  - Support the Volto frontend?
  - `true`
  - —
  - —
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

The post-generation hook:

- removes the `browser` package when `feature_headless` is yes, or the `serializers` package when it's no;
- creates the namespace packages of `python_package_name` in `src`;
- formats the code;
- initializes a git repository.

Then the template runs these sub-templates:

| Sub-template | Generates | When |
|---|---|---|
| `docs/starter` | `docs`: a documentation scaffold | `initialize_documentation` is yes |
| `ide/vscode` | `.vscode`: Visual Studio Code settings | `initialize_ci` is yes |
| `ci/gh_backend_addon` | `.github`: GitHub Actions workflows | `initialize_ci` is yes |

When `project`, `aurora_cmfplone`, or `monorepo_addon` run `backend_addon` as a sub-template, the hook skips the namespace packages, which the parent template creates, and the parent template removes the `.git` folder from `backend`.

## Generated files

With the default answers, the template generates these files, three levels deep:

% tree:begin

```text
collective.addon/
├── .cookieplone.json
├── .editorconfig
├── .flake8
├── .github/
│   ├── dependabot.yml
│   ├── instructions/
│   │   ├── docs.instructions.md
│   │   └── general/
│   └── workflows/
│       ├── changelog.yml
│       ├── config.yml
│       └── main.yml
├── .gitignore
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json
├── bobtemplate.cfg
├── CHANGELOG.md
├── CONTRIBUTORS.md
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
├── instance.yaml
├── LICENSE.GPL
├── LICENSE.md
├── Makefile
├── mx.ini
├── news/
│   ├── .changelog_template.jinja
│   └── .gitkeep
├── pyproject.toml
├── README.md
├── scripts/
│   └── create_site.py
├── src/
│   └── collective/
│       └── addon/
└── tests/
    ├── conftest.py
    └── setup/
        ├── test_setup_install.py
        └── test_setup_uninstall.py
```

% tree:end

## Next steps

The generated `README.md` lists uv, Make, and git as prerequisites, and Docker as optional.
From the add-on folder, install the add-on and create a Plone site:

```console
make install
make create-site
```

Start Plone at `http://localhost:8080`:

```console
make start
```

`make help` lists the other targets, such as `make test`.
