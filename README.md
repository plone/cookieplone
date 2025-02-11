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

</div>

Welcome to Cookieplone, a powerful wrapper around Cookiecutter designed to streamline the development of Plone codebases.
Whether you're building a backend add-on, a new Volto add-on, a full project with both backend and frontend, Cookieplone simplifies the process using robust Cookiecutter templates.

## Key features 🌟

Cookieplone offers the following key features for each audience.

### For users

- **One stop for all Plone templates**: Cookieplone helps you find the correct template to start your new Plone project.
- **Simplified usage**: Cookieplone provides an enhanced experience over standard Cookiecutter usage by offering predefined sane defaults and a unified approach to generating various Plone projects.
- **Batteries included**: No need to install lots of dependencies. Run `pipx run cookieplone`, and you will quickly generate your codebase.


### For template creators

- **Built-in validators**: Includes built-in validators to ensure user inputs are correct.
- **Jinja2 filters**: Includes Jinja2 filters for advanced template control.
- **Sub-templates**: Mechanism to easily instantiate "sub templates" within cookiecutter hooks -- i.e. post_gen_hook -- , facilitating greater code reuse.


## Installation 💾

First, ensure you have Python, pip, and pipx installed on your system.

See [how to install these and check Plone's prerequisites](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation).
Set up your system with [Plone's prerequisites](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation).
Then install Cookieplone using `pipx`:

```shell
# pipx is strongly recommended.
pipx install cookieplone
```

Or, if pipx is not an option, you can install Cookieplone in your Python user directory.

```shell
python -m pip install --user cookieplone
```

## Usage 🛠️

To see all available template options, run:

```shell
pipx run cookieplone
```

Cookieplone will walk you through the necessary steps, using sensible defaults and offering customization options where needed.

### Use options to avoid prompts

Cookieplone will ask a lot of questions.
You can use some of its options to avoid repeatedly entering the same values.

#### `--no-input`

You can use the [`--no-input`](https://cookiecutter.readthedocs.io/en/latest/cli_options.html#cmdoption-cookiecutter-no-input) option to make Cookieplone not prompt for parameters and only use `cookiecutter.json` file content.

#### `--replay` and `--replay-file`

You can use the options [`--replay`](https://cookiecutter.readthedocs.io/en/latest/cli_options.html#cmdoption-cookiecutter-replay) and [`--replay-file`](https://cookiecutter.readthedocs.io/en/latest/cli_options.html#cmdoption-cookiecutter-replay-file) to not prompt for parameters and only use information entered previously or from a specified file.
See [Replay Project Generation](https://cookiecutter.readthedocs.io/en/latest/advanced/replay.html) in the cookiecutter documentation for more information.

### Specify a template

You can also specify other templates.

| Template | Description | Command |
| --- | --- | --- |
| **backend_addon** | Create a Plone add-on to be used with the backend. | `pipx run cookieplone backend_addon ` |
| **frontend_addon** | Create a Plone add-on to be used with the frontend. | `pipx run cookieplone frontend_addon ` |

The updated list of templates can be found at the [cookieplone-templates](https://github.com/plone/cookieplone-templates) repository.

### Configure Cookieplone

| Environment Variable | Description | Example |
| --- | --- | --- |
| **COOKIEPLONE_REPOSITORY** | Where to look for templates to be used. | `COOKIEPLONE_REPOSITORY=/home/plone/cookieplone-templates/ pipx run cookieplone` |
| **COOKIEPLONE_REPOSITORY_TAG** | Which tag/branch to use from a remote repository. | `COOKIEPLONE_REPOSITORY_TAG=experimental pipx run cookieplone` |
| **COOKIEPLONE_REPO_PASSWORD** | Password to use when using a remote repository that is password protected. | `COOKIEPLONE_REPO_PASSWORD=very-secure pipx run cookieplone` |

## Contribute 🤝

We welcome contributions to Cookieplone.

You can create an issue in the issue tracker, or contact a maintainer.

- [Issue Tracker](https://github.com/plone/cookieplone/issues)
- [Source Code](https://github.com/plone/cookieplone/)

### Development requirements

- Python 3.10 or later
- [Hatch](https://hatch.pypa.io/)

### Setup

Install all development dependencies, including Hatch, and create a local virtual environment with the following command.

```shell
make install
```

### Run the checked out branch of Cookieplone

```shell
hatch run cookieplone
```

### Check and format the codebase

```shell
make check
```

### Run tests

[`pytest`](https://docs.pytest.org/) is this package's test runner.

Run all tests with the following command.

```shell
make test
```

Run all tests, but stop on the first error and open a `pdb` session with the following command.

```shell
hatch run test -x --pdb
```

Run only tests that match `test_run_sanity_checks_fail` with the following command.

```shell
hatch run test -k test_run_sanity_checks_fail
```

Run only tests that match `test_run_sanity_checks_fail`, but stop on the first error and open a `pdb` session with the following command.

```shell
hatch run test -k test_run_sanity_checks_fail -x --pdb
```

## Support 📢

For support, questions, or more detailed documentation, visit the [official Cookieplone repository](https://github.com/plone/cookieplone).

Thank you for choosing Cookieplone for your Plone development needs!


## This project is supported by

<p align="left">
    <a href="https://plone.org/foundation/">
      <img alt="Plone Foundation Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-foundation.png">
    </a>
</p>

## License

The project is released under the [MIT License](./LICENSE).
