REGISTRIES = {"docker_hub": "", "github": "ghcr.io/", "gitlab": "registry.gitlab.com/"}


def image_prefix(registry: str) -> str:
    """Return the image prefix to be used based on the registry used."""
    return REGISTRIES.get(registry, "")
