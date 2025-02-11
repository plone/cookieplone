# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
PLONE_MIN_VERSION = "6"

SUPPORTED_PYTHON_VERSIONS = [
    "3.10",
    "3.11",
    "3.12",
    "3.13",
]

DEFAULT_NODE = 22
SUPPORTED_NODE_VERSIONS = [
    "20",
    "22",
]


VOLTO_MIN_VERSION = "18.0.0-alpha.1"
VOLTO_NODE = {
    18: 22,
}
MIN_DOCKER_VERSION = "20.10"

## DEFAULT
COOKIEPLONE_REPO = "https://github.com/plone/cookieplone"
TEMPLATES_REPO = "https://github.com/plone/cookieplone-templates"
REPO_DEFAULT = "gh:plone/cookieplone-templates"

## Config
QUIET_MODE_VAR = "COOKIEPLONE_QUIET_MODE_SWITCH"
REPO_LOCATION = "COOKIEPLONE_REPOSITORY"
REPO_TAG = "COOKIEPLONE_REPOSITORY_TAG"
REPO_PASSWORD = "COOKIEPLONE_REPO_PASSWORD"  # noQA:S105
