def _is_scoped_package(name: str) -> bool:
    """Check if package is scoped."""
    return name.startswith("@") and "/" in name


def parse_package_name(name: str) -> tuple[str, str]:
    """Parse a NPM name and returns organization and package_name."""
    org = ""
    package_name = name
    if _is_scoped_package(name):
        org, package_name = name.split("/", 1)
    return org, package_name


def unscopped_package_name(name: str) -> str:
    """Return the unscopped package name for an NPM package."""
    _, package_name = parse_package_name(name)
    return package_name
