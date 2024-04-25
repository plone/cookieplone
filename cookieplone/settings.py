# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
PLONE_MIN_VERSION = "6"

SUPPORTED_PYTHON_VERSIONS = [
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
]

DEFAULT_NODE = 18
SUPPORTED_NODE_VERSIONS = [
    "16",
    "17",
    "18",
    "19",
    "20",
]


VOLTO_MIN_VERSION = "16"
VOLTO_NODE = {
    16: 16,
    17: DEFAULT_NODE,
    18: 20,
}
MIN_DOCKER_VERSION = "20.10"


## Config
QUIET_MODE_VAR = "COOKIEPLONE_QUIET_MODE_SWITCH"
REPO_LOCATION = "COOKIEPLONE_REPOSITORY"
REPO_PASSWORD = "COOKIEPLONE_REPO_PASSWORD"  # noQA:S105
