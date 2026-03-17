# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from dataclasses import dataclass


@dataclass
class PythonVersionSupport:
    """Python version support for Plone."""

    supported: list[str]
    earliest: str
    latest: str


PLONE_MIN_VERSION = "6"

SUPPORTED_PYTHON_VERSIONS = [
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    "3.14",
]

# A matrix of Plone and Python version support.
# For each version of Plone, its Python support is a tuple,
# where the corresponding elements are
# a list of supported Python versions,
# its earliest supported Python version, and
# its latest supported Python version.
PLONE_PYTHON = {
    "6.0": PythonVersionSupport(
        [
            "3.10",
            "3.11",
            "3.12",
        ],
        "3.10",
        "3.12",
    ),
    "6.1": PythonVersionSupport(
        [
            "3.10",
            "3.11",
            "3.12",
            "3.13",
        ],
        "3.10",
        "3.13",
    ),
}

DEFAULT_NODE = 24
SUPPORTED_NODE_VERSIONS = [
    "20",
    "22",
    "24",
]


VOLTO_MIN_VERSION = "18.0.0-alpha.43"
VOLTO_NODE = {
    18: 22,
    19: 24,
}
MIN_DOCKER_VERSION = "20.10"

# DEFAULT
COOKIEPLONE_REPO = "https://github.com/plone/cookieplone"
TEMPLATES_REPO = "https://github.com/plone/cookieplone-templates"
REPO_DEFAULT = "gh:plone/cookieplone-templates"

# Config
QUIET_MODE_VAR = "COOKIEPLONE_QUIET_MODE_SWITCH"
REPO_LOCATION = "COOKIEPLONE_REPOSITORY"
REPO_TAG = "COOKIEPLONE_REPOSITORY_TAG"
REPO_PASSWORD = "COOKIEPLONE_REPO_PASSWORD"  # noQA:S105

# Connectivity
REQUESTS_TIMEOUT = 10

# Allowed computed keys in config file
CONFIG_COMPUTED_KEYS = [
    "__generator_sha",
    "__generator_signature",
    "__cookieplone_template",
    "__cookieplone_repository_path",
]

# Root key used for templates
DEFAULT_DATA_KEY = "cookiecutter"

# Cookieplone answers
COOKIEPLONE_ANSWERS_FILE = ".cookieplone.json"

# Questions validators
## The keys are the variable names in cookiecutter.json/cookieplone.json,
## and the values are the import paths to the validator functions.
DEFAULT_VALIDATORS = {
    "plone_version": "cookieplone.validators.plone_version",
    "volto_version": "cookieplone.validators.volto_version",
    "python_package_name": "cookieplone.validators.python_package_name",
    "hostname": "cookieplone.validators.hostname",
    "language_code": "cookieplone.validators.language_code",
}

# Jinja2 default extensions
DEFAULT_EXTENSIONS = [
    "cookiecutter.extensions.JsonifyExtension",
    "cookiecutter.extensions.RandomStringExtension",
    "cookiecutter.extensions.SlugifyExtension",
    "cookiecutter.extensions.TimeExtension",
    "cookiecutter.extensions.UUIDExtension",
]
