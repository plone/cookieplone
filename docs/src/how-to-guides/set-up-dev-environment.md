---
myst:
  html_meta:
    "description": "How to set up a development environment for Cookieplone, find your way around the code, work on the documentation, and add a changelog entry."
    "property=og:description": "How to set up a development environment for Cookieplone, find your way around the code, work on the documentation, and add a changelog entry."
    "property=og:title": "Set up a development environment"
    "keywords": "Cookieplone, development, contributing, make install, make test, make lint, documentation, towncrier"
---

# Set up a development environment

This guide sets up a local environment for working on the Cookieplone codebase and its documentation.

## Prerequisites

- Python 3.10 or later.
- [uv](https://docs.astral.sh/uv/).
- git.
- [Hatch](https://hatch.pypa.io/), which `make install` uses to install the pre-commit hooks.
- Node.js 20, 22, or 24, to run `make docs-snippets`.

## Clone the repository

```console
git clone https://github.com/plone/cookieplone.git
cd cookieplone
```

## Install dependencies

```console
make install
```

This command runs `uv sync`, which creates the virtual environment in `.venv` with the development dependencies.
In a git clone, it then installs the pre-commit hooks with `hatch run pre-commit install`.

## Run the test suite

```console
make test
```

All tests must pass before you submit a pull request.
To run one test file or one test, call pytest directly:

```console
uv run pytest tests/utils/test_git.py -v
uv run pytest tests/utils/test_git.py::test_repo_from_path -v
```

## Run the linters

```console
make lint
```

This command runs the pre-commit hooks on all files: file checks, `ruff`, `ruff format`, `codespell`, `pyroma`, and `check-python-versions`.
`make format` runs the same hooks, which fix what they can.

## Find your way around the code

| Location | What it does |
|---|---|
| `cookieplone/cli/` | The `cookieplone` command, its options, and the parsing of `key=value` pairs. |
| `cookieplone/repository.py` | Finds, clones, and checks template repositories: `cookieplone-config.json`, `extends`, `config.min_version`, the fallback branch, and the `pre_prompt` hook. |
| `cookieplone/config/` | Reads the user configuration (`user.py`) and a template's `cookieplone.json` (`state.py`, `v1.py`, `v2.py`), merges `extends` (`merge.py`), and holds the JSON Schemas (`schemas/`). |
| `cookieplone/wizard.py` | Builds the `tui_forms` form and chooses the renderer. |
| `cookieplone/generator/` | `generate()`, and the run of the wizard and of Cookiecutter's file generation (`main.py`). |
| `cookieplone/filters/` | The Jinja2 filters. |
| `cookieplone/validators/`, `cookieplone/utils/validators.py` | The built-in validators. |
| `cookieplone/utils/` | Helpers for Cookieplone and template hooks, such as `post_gen.py`, `subtemplates.py`, `git.py`, `plone.py`, `answers.py`, `sanity.py`, `commands/`, and `versions.py`. |
| `cookieplone/templates/` | The pytest plugins for testing template repositories. |
| `cookieplone/settings.py` | Default values and the names of environment variables. |
| `tests/` | The test suite, laid out like the `cookieplone` package. |

{doc}`/reference/api/index` documents the functions that template hooks use, and {doc}`/concepts/how-cookieplone-works` describes a run from start to finish.

## Work on the documentation

The documentation is a Sphinx site written in MyST Markdown, in `docs/src/`.
Its pages follow four sections: `tutorials/`, `how-to-guides/`, `reference/`, and `concepts/`.
Pages include longer samples from `docs/_examples/`, and the scripts in `docs/_checks/` generate those samples to prove they work.

The Documentation workflow (`.github/workflows/docs.yml`) builds and checks the site on every push.
After a push to `main`, it publishes the site to <https://plone.github.io/cookieplone/>.

### Add a page

1.  Create a Markdown file in the section's folder, and start it with the `myst` front matter that the other pages use: `description`, `property=og:description`, `property=og:title`, and `keywords`.
2.  Add the file name to the `toctree` of the section's `index.md`.
3.  Build the site and fix every warning:

    ```console
    make docs-html SPHINXOPTS="-W --keep-going"
    ```

    The site sets `nitpicky = True`, so every cross-reference, such as `{py:func}`, must resolve.
4.  Run Vale:

    ```console
    make docs-vale
    ```

    Vale uses the Microsoft style and the vocabulary in `docs/styles/config/vocabularies/Plone/accept.txt`.
    Add a correct term that Vale doesn't know to that file.

To preview the site while you edit, run `make docs-livehtml`, and open `http://127.0.0.1:8050`.

### Check the documentation

| Command | Checks |
|---|---|
| `make docs-html SPHINXOPTS="-W --keep-going"` | The build, with warnings as errors. |
| `make docs-vale` | Style, grammar, and spelling. |
| `make docs-linkcheck` | Every external link. |
| `make docs-snippets` | The template reference pages, the example repositories, and the first project tutorial, against real generations. |
| `make docs-test` | Cleans the build, then runs Vale, reports broken links, and runs doctest. |

`make docs-snippets` clones [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) at the branch in `DOCS_TEMPLATES_REF`, `next` by default.
It needs network access, uv, Node.js, and git.

### Update the template reference pages

{doc}`/reference/templates/index` pages are partly generated from `cookieplone-templates`.
The questions table and the file tree of each page sit between `% questions:begin` and `% questions:end`, and between `% tree:begin` and `% tree:end`.
After a change in `cookieplone-templates`, generate every template, and rewrite those blocks:

```console
uv run python docs/_checks/inventory_templates.py
uv run python docs/_checks/template_pages.py --write
```

The first command writes the inventory to `docs/_templates-inventory/`, which git ignores.
Update the rest of each page, such as requirements and next steps, by hand.
The tree in {doc}`/tutorials/create-your-first-plone-project` has its own command, `docs/_checks/run_tutorial.sh --write`.

## Add a changelog entry

Cookieplone uses [towncrier](https://towncrier.readthedocs.io/en/stable/).
Each pull request to `main` adds a news fragment to `news/`, and the Changelog check workflow fails without one.
Name the file after the issue number and the type of change, such as `news/212.documentation`.
The types are `breaking`, `feature`, `bugfix`, `internal`, `documentation`, and `tests`.

Write the entry in the past tense, and end it with your GitHub handle:

```text
Added a troubleshooting entry for offline generation. @jane-doe
```

To preview the next changelog, run `make changelog`.

## Release

Maintainers release Cookieplone with `make release`.
It runs `prerelease` and `release` from zest.releaser, builds the package with `uv build`, publishes it with `uv publish`, and runs `postrelease`.
During the release, towncrier writes the news fragments into `CHANGES.md`.

## Related pages

- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator.
