# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
REGISTRIES = {"docker_hub": "", "github": "ghcr.io/", "gitlab": "registry.gitlab.com/"}


def image_prefix(registry: str) -> str:
    """Return the image prefix to be used based on the registry used."""
    return REGISTRIES.get(registry, "")
