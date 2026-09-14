<p align="center">
    <img alt="Plone Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-logo.png">
</p>

<h1 align="center">
  Cookieplone 🍪
</h1>


<div align="center">

[![PyPI](https://img.shields.io/pypi/v/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - License](https://img.shields.io/github/license/Plone/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - Status](https://img.shields.io/pypi/status/cookieplone)](https://pypi.org/project/cookieplone/)

[![Tests](https://github.com/plone/cookieplone/actions/workflows/main.yml/badge.svg)](https://github.com/plone/cookieplone/actions/workflows/main.yml)

[![GitHub contributors](https://img.shields.io/github/contributors/plone/cookieplone)](https://github.com/plone/cookieplone)
[![GitHub Repo stars](https://img.shields.io/github/stars/plone/cookieplone?style=social)](https://github.com/plone/cookieplone)

[![Documentation](https://img.shields.io/badge/Cookieplone-Docs-blue?style=flat&logo=sphinx&link=https%3A%2F%2Fplone.github.io%2Fcookieplone%2F)](https://plone.github.io/cookieplone/)


</div>

Welcome to Cookieplone, your starting point for every Plone project.
Whether you're building an add-on, starting a new project, or even creating your own Plone Distribution, Cookieplone simplifies the process by using templates maintained by the Plone Community in [cookieplone-templates](https://github.com/plone/cookieplone-templates).

Read the full documentation at [plone.github.io/cookieplone](https://plone.github.io/cookieplone/).

## Key features 🌟

Cookieplone offers the following key features for each audience.

### For users

- **One stop for all Plone templates**: Cookieplone lists the official templates by category, and helps you pick the one for your new Plone project.
- **Simplified usage**: Cookieplone asks only the questions a template needs, with sensible defaults, checks your answers, and shows them for review before it generates anything.
- **No installation needed**: Run `uvx cookieplone`, and you will quickly generate your codebase.

### For template creators

- **Template repositories**: Group templates in a repository with a `cookieplone-config.json`, hide internal templates, and extend another repository, such as `cookieplone-templates`, instead of forking it.
- **Built-in validators**: Includes built-in validators to ensure user inputs are correct.
- **Jinja2 filters**: Includes Jinja2 filters for advanced template control.
- **Sub-templates and hook helpers**: Generate sub-templates and run common post-generation actions from your template's hooks, facilitating greater code reuse.
- **pytest plugins**: Test your templates with fixtures that Cookieplone provides.

See [Create a template](https://plone.github.io/cookieplone/tutorials/create-a-template.html) to get started.

## Installation 💾

Cookieplone needs Python 3.10 or later, [uv](https://docs.astral.sh/uv/getting-started/installation/), and git.
Each template checks for the other tools it needs, such as Node.js or Docker, before it asks its first question.

See [Install Cookieplone](https://plone.github.io/cookieplone/install.html) for the requirements of each template, and Plone's [Prerequisites for installation](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) for your operating system.

## Usage 🛠️

Use `uvx` (command installed by uv) to run `cookieplone` and choose a template from its menu:

```shell
uvx cookieplone
```

It is also possible to run a specific version of Cookieplone:

```shell
uvx cookieplone@2.0.0
```

Cookieplone will walk you through the necessary steps, using sensible defaults and offering customization options where needed.
The tutorial [Create your first Plone project](https://plone.github.io/cookieplone/tutorials/create-your-first-plone-project.html) walks through a complete run.

### Try a prerelease version

Plain `uvx cookieplone` (and `uvx cookieplone@latest`) always picks the latest **stable** release — prerelease versions (`aN`, `bN`, `rcN`, `.devN`) are excluded by default, following [PEP 440](https://peps.python.org/pep-0440/) and the `uv` resolver defaults.

To opt in to a prerelease — for example, `2.1.0a1` — pin the exact version:

```shell
uvx cookieplone@2.1.0a1
```

Or allow the resolver to consider any prerelease:

```shell
uvx --prerelease=allow cookieplone
```

If you previously installed Cookieplone with `uv tool install`, reinstall the tool explicitly so the cached stable install is replaced:

```shell
uv tool install --reinstall --prerelease=allow cookieplone
```

You can confirm which version is active with:

```shell
uvx cookieplone --version
```

See [Use a prerelease version of Cookieplone](https://plone.github.io/cookieplone/how-to-guides/use-a-prerelease-version.html) for details.

### Specify a template

Pass a template ID to skip the menu:

```shell
uvx cookieplone project
```

These are the templates of [cookieplone-templates](https://github.com/plone/cookieplone-templates):

| Template | Description |
| --- | --- |
| [`project`](https://plone.github.io/cookieplone/reference/templates/project.html) | Plone 6 Project |
| [`aurora_cmfplone`](https://plone.github.io/cookieplone/reference/templates/aurora_cmfplone.html) | Plone Aurora (alpha) with Plone backend |
| [`volto_nick`](https://plone.github.io/cookieplone/reference/templates/volto_nick.html) | Plone Volto using Nick as backend |
| [`aurora_nick`](https://plone.github.io/cookieplone/reference/templates/aurora_nick.html) | Plone Aurora (alpha) using Nick as backend |
| [`aurora_nick_embedded`](https://plone.github.io/cookieplone/reference/templates/aurora_nick_embedded.html) | Plone Aurora (alpha) using Nick as an embedded library (experimental) |
| [`monorepo_addon`](https://plone.github.io/cookieplone/reference/templates/monorepo_addon.html) | Plone 6 Add-on (Frontend and Backend) |
| [`backend_addon`](https://plone.github.io/cookieplone/reference/templates/backend_addon.html) | Plone 6 Backend Add-on (Python) |
| [`frontend_addon`](https://plone.github.io/cookieplone/reference/templates/frontend_addon.html) | Plone 6 Frontend Add-on |
| [`aurora_addon`](https://plone.github.io/cookieplone/reference/templates/aurora_addon.html) | Plone Aurora Frontend Add-on |
| [`documentation_starter`](https://plone.github.io/cookieplone/reference/templates/documentation_starter.html) | Documentation scaffold for Plone projects |

Each template's page lists its requirements, questions, and generated files.
`uvx cookieplone --all` also shows the hidden templates.

### Use options to avoid prompts

Cookieplone will ask a lot of questions.
You can use some of its options to avoid repeatedly entering the same values.

#### `key=value`

Pass answers after the template ID, such as `uvx cookieplone project title="My Site"`.
In an interactive run, they pre-fill the questions.
See [Set answers with extra context](https://plone.github.io/cookieplone/how-to-guides/use-extra-context.html).

#### `--answers-file`

Point `--answers-file` (or `--answers`) to a JSON file with the answers you want to use to pre-populate default values.

#### `--no-input`

Use `--no-input` to make Cookieplone not prompt for questions and use the default values, the answers file, and `key=value` pairs instead.
Cookieplone still validates each value.

#### `--replay` and `--replay-file`

Use `--replay` to generate a project again with the answers of your previous run of the same template, or `--replay-file` to read them from a file.
See [Answers and replay](https://plone.github.io/cookieplone/concepts/answers-and-replay.html).

All options are listed in the [CLI reference](https://plone.github.io/cookieplone/reference/cli.html).

### Configure Cookieplone

| Environment Variable | Description | Example |
| --- | --- | --- |
| **COOKIEPLONE_REPOSITORY** | The template repository to use: a local path, a git URL, a zip archive, or an abbreviation such as `gh:`. | `COOKIEPLONE_REPOSITORY=/home/plone/cookieplone-templates/ uvx cookieplone` |
| **COOKIEPLONE_REPOSITORY_TAG** | Which tag or branch to use from a git repository. | `COOKIEPLONE_REPOSITORY_TAG=next uvx cookieplone` |
| **COOKIEPLONE_REPO_PASSWORD** | Password of a password-protected zip archive used as the template repository. | `COOKIEPLONE_REPO_PASSWORD=very-secure uvx cookieplone` |
| **COOKIEPLONE_RENDERER** | The renderer for the questions: `cookiecutter`, `rich`, or `stdlib`. | `COOKIEPLONE_RENDERER=rich uvx cookieplone` |

See the [environment variables reference](https://plone.github.io/cookieplone/reference/environment-variables.html) for all variables.
If something goes wrong, check [Troubleshooting](https://plone.github.io/cookieplone/troubleshooting.html).

## Contribute 🤝

We welcome contributions to Cookieplone.

You can create an issue in the issue tracker, or contact a maintainer.
Report issues with a template, or propose a new one, in the [cookieplone-templates](https://github.com/plone/cookieplone-templates) repository.

- [Issue Tracker](https://github.com/plone/cookieplone/issues)
- [Source Code](https://github.com/plone/cookieplone/)
- [Templates](https://github.com/plone/cookieplone-templates)

### Branches

| Branch | Target version | Status |
| --- | --- | --- |
| **main** | 2.x | Active development |
| **1.x** | 1.x (patch and minor) | Maintenance only |

All new feature development targets the `main` branch.
The `1.x` branch is in maintenance mode and only receives bug fixes and minor improvements released as 1.x versions.

### Development requirements

See [Installation](#installation-), and [Set up a development environment](https://plone.github.io/cookieplone/how-to-guides/set-up-dev-environment.html) for the full guide.

### Setup

Create a local Python virtual environment and install the pre-commit hooks with the following command.

```shell
make install
```

### Run the checked out branch of Cookieplone

```shell
uv run cookieplone
```

### Check and format the codebase

```shell
make lint
```

`make format` runs the same checks and fixes what it can.

### Run tests

[`pytest`](https://docs.pytest.org/) is this package's test runner.

Run all tests with the following command.

```shell
make test
```

Run all tests, but stop on the first error and open a `pdb` session with the following command.

```shell
uv run pytest -x --pdb
```

Run only tests that match `test_run_sanity_checks_fail` with the following command.

```shell
uv run pytest -k test_run_sanity_checks_fail
```

Run only tests that match `test_run_sanity_checks_fail`, but stop on the first error and open a `pdb` session with the following command.

```shell
uv run pytest -k test_run_sanity_checks_fail -x --pdb
```

### Work on the documentation

Build the documentation, and run its checks, with the following commands.

```shell
make docs-html
make docs-test
```

## Support 📢

For support and questions, read the [documentation](https://plone.github.io/cookieplone/), search the [issue tracker](https://github.com/plone/cookieplone/issues), or ask in the [Plone Community Forum](https://community.plone.org/).

Thank you for choosing Cookieplone for your Plone development needs!


## This project is supported by

<p align="left">
    <a href="https://plone.org/foundation/">
      <img alt="Plone Foundation Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-foundation.png">
    </a>
</p>

## License

The project is released under the [MIT License](./LICENSE).
