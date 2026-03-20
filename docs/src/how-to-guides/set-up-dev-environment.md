---
myst:
  html_meta:
    "description": "How to set up a local development environment for contributing to cookieplone."
    "property=og:description": "How to set up a local development environment for contributing to cookieplone."
    "property=og:title": "Set up a development environment"
    "keywords": "Cookieplone, development, contributing, make install, make test, make lint"
---

# Set up a development environment

This guide walks you through setting up a local environment for working on the Cookieplone codebase.

## Prerequisites

- Python 3.10 or later.
- [uv](https://docs.astral.sh/uv/) installed.
- git installed.

## Clone the repository

```console
git clone https://github.com/plone/cookieplone.git
cd cookieplone
```

## Install dependencies

```console
make install
```

This creates a virtual environment and installs Cookieplone with all development dependencies using `uv`.

## Run the test suite

```console
make test
```

All tests must pass before submitting a pull request.

## Run the linters

```console
make lint
```

This runs `ruff` (format check and lint) and `pyupgrade` over the codebase.
Fix any reported issues before submitting.

## Run a single test file

```console
uv run pytest tests/path/to/test_file.py -v
```

## Run a specific test

```console
uv run pytest tests/path/to/test_file.py::test_function_name -v
```

## Build the documentation

```console
make docs-html
```

The output is written to `docs/_build/html/`.

## Run Vale on the documentation

```console
make docs-vale
```

This lints the documentation for style issues using the Microsoft style guide.

## Full documentation test

```console
make docs-test
```

This runs both the Sphinx build and Vale.
All errors must be resolved before submitting documentation changes.

## Related pages

- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator.
