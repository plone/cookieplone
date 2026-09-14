---
myst:
  html_meta:
    "description": "How to run or install Cookieplone, and which tools your computer needs."
    "property=og:description": "How to run or install Cookieplone, and which tools your computer needs."
    "property=og:title": "Install Cookieplone"
    "keywords": "Cookieplone, install, uv, uvx, uv tool, virtual environment, Python, git, Node.js, Docker"
---

# Install Cookieplone

Cookieplone is a command line application written in Python.
You can run it without installing it, install it as a tool, or install it in a virtual environment.

## Requirements

Cookieplone needs:

- Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- [uv](https://docs.astral.sh/uv/getting-started/installation/), to run Cookieplone with `uvx` or to install it.
- [git](https://git-scm.com/), to download templates from a git repository, such as the default [`cookieplone-templates`](https://github.com/plone/cookieplone-templates).

Before it asks its first question, each official template checks your computer for the tools it needs.
When a required tool is missing, the template stops.

| Template | uv | Node.js | git | Docker |
|---|---|---|---|---|
| `project`, `aurora_cmfplone`, `monorepo_addon` | Required | Required | Required | Optional, version 26 or later |
| `volto_nick`, `aurora_nick`, `aurora_nick_embedded` | — | Required | Required | — |
| `backend_addon` | Required | — | Required | — |
| `frontend_addon`, `aurora_addon` | — | Required | Required | — |
| `documentation_starter` | — | — | — | — |

Each template's page in {doc}`/reference/templates/index` lists the Node.js versions it accepts.
To work on a generated project, follow the prerequisites in its `README.md`.

:::{note}
The Cookieplone test suite runs on Linux.
For operating system requirements, including Windows, see [Prerequisites for installation](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) in the Plone documentation.
:::

## Run Cookieplone without installing it

`uvx` downloads Cookieplone and runs it:

```console
uvx cookieplone
```

Without a version, `uvx` runs the latest stable release.
To try a prerelease, see {doc}`/how-to-guides/use-a-prerelease-version`.

To run a specific release, add its version after `@`:

```console
uvx cookieplone@2.0.0
```

To ask for the latest stable release explicitly, use `@latest`:

```console
uvx cookieplone@latest
```

## Install Cookieplone as a tool

Install Cookieplone with `uv tool install`, to use the `cookieplone` command without `uvx`:

```console
uv tool install cookieplone
```

If uv warns that its tool directory isn't on your `PATH`, run the command it suggests.

Upgrade the tool to the latest release:

```console
uv tool upgrade cookieplone
```

## Install Cookieplone in a virtual environment

Create a virtual environment, activate it, and install Cookieplone into it:

```console
uv venv
source .venv/bin/activate
uv pip install cookieplone
```

## Check the version

Print the version of the Cookieplone you run:

```console
cookieplone --version
```

With `uvx`, run `uvx cookieplone --version`.
The first line shows the Cookieplone version, where it's installed, and the Cookiecutter and Python versions it uses.

## Next steps

- {doc}`/tutorials/create-your-first-plone-project`: generate your first project.
- {doc}`/reference/compatibility`: the versions Cookieplone 2.0 and the official templates support.
