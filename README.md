<p align="center">
    <img alt="Plone Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-logo.png">
</p>

<h1 align="center">
  cookieplone 🍪
</h1>


<div align="center">

[![PyPI](https://img.shields.io/pypi/v/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - License](https://img.shields.io/pypi/l/cookieplone)](https://pypi.org/project/cookieplone/)
[![PyPI - Status](https://img.shields.io/pypi/status/cookieplone)](https://pypi.org/project/cookieplone/)


[![Tests](https://github.com/plone/cookieplone/actions/workflows/main.yml/badge.svg)](https://github.com/plone/cookieplone/actions/workflows/main.yml)

[![GitHub contributors](https://img.shields.io/github/contributors/plone/cookieplone)](https://github.com/plone/cookieplone)
[![GitHub Repo stars](https://img.shields.io/github/stars/plone/cookieplone?style=social)](https://github.com/plone/cookieplone)

</div>

Welcome to Cookieplone, a powerful wrapper around Cookiecutter designed to streamline the development of Plone codebases. Whether you're building a backend addon, a new Volto addon, a full project with both backend and frontend, or even documentation, Cookieplone simplifies the process using robust Cookiecutter templates.

## Key Features 🌟

### For Users

- **One Stop for All Plone Templates**: Cookieplone helps you to find the correct template to start your new Plone project.

- **Simplified Usage**: Cookieplone provides an enhanced experience over standard Cookiecutter usage by offering predefined sane defaults and a unified approach to generating various Plone projects.

- **Batteries Included**: No need to install lot's of dependencies, just run `pipx run cookieplone` and you will be able to quickly generate your codebase.


### For Template Creators

- **Built-in Validators**: Includes built-in validators to ensure user inputs are correct.
- **Jinja2 Filters**: Includes Jinja2 filters for advanced template control.
- **Sub-Templates**: Mechanism to easily instantiate "sub templates" within cookiecutter hooks -- i.e. post_gen_hook -- , facilitating greater code reuse.


## Installation 💾

First, ensure you have Python, pip and pipx installed on your system.

Then install cookieplone using `pipx`:

```bash
# pipx is strongly recommended.
pipx install cookieplone
```

Or, if pipx is not an option, you can install cookieplone in your Python user directory.

```bash
python -m pip install --user cookieplone
```

## Usage 🛠️

### Running Cookieplone

To see all available template options, just run:

```bash
pipx run cookieplone
```

Cookieplone will walk you through the necessary steps, using sensible defaults and offering customization options where needed.

### Specifying a template

You can also specify other templates like:

| Template | Description | Command |
| --- | --- | --- |
| **project** | Create a Plone project with Backend and frontend. | `pipx run cookieplone project ` |
| **plone_addon** | Create a Plone add-on to be used with the backend. | `pipx run cookieplone plone_addon ` |
| **volto_addon** | Create a Plone add-on to be used with the frontend. | `pipx run cookieplone volto_addon ` |

### Configuring cookieplone

| Environment Variable | Description | Example |
| --- | --- | --- |
| **COOKIEPLONE_REPOSITORY** | Where to look for templates to be used. | `COOKIEPLONE_REPOSITORY=/home/plone/cookiecutter-plone/ pipx run cookieplone` |
| **COOKIEPLONE_REPOSITORY_REF** | Which tag/branch to use from a remote repository. | `COOKIEPLONE_REPOSITORY_REF=experimental pipx run cookieplone` |
| **COOKIEPLONE_REPO_PASSWORD** | Password to use when using a remote repository that is password protected. | `COOKIEPLONE_REPO_PASSWORD=very-secure pipx run cookieplone` |

## Contributing 🤝

We welcome contributions to `cookieplone`.

You can create an issue in the issue tracker, or contact a maintainer.

- [Issue Tracker](https://github.com/plone/cookieplone/issues)
- [Source Code](https://github.com/plone/cookieplone/)

### Development requirements

- Python 3.10 or later
- [`hatch`](https://hatch.pypa.io/)

### Setup

Install all development dependencies -- including `hatch` -- and create a local virtual environment with:

```bash
make install
```

### Check / Format codebase

```bash
make check
```

### Run tests

Testing of this package is done with [`pytest`](https://docs.pytest.org/).

Run all tests with:

```bash
make test
```

Run all tests but stop on the first error and open a `pdb` session:

```bash
hatch run test -x --pdb
```

Run only tests that match `test_run_sanity_checks_fail`:

```bash
hatch run test -k test_run_sanity_checks_fail
```

Run only tests that match `test_run_sanity_checks_fail`, but stop on the first error and open a `pdb` session:

```bash
hatch run test -k test_run_sanity_checks_fail -x --pdb
```

## Support 📢

For support, questions, or more detailed documentation, visit the [official Cookieplone repository](https://github.com/plone/cookieplone).

Thank you for choosing Cookieplone for your Plone development needs!


## This project is supported by

<p align="left">
    <a href="https://plone.org/foundation/">
      <img alt="Plone Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-foundation.png">
    </a>
</p>

## License
The project is released under the [MIT License](./LICENSE)
