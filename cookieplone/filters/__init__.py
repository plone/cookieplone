from cookiecutter.utils import simple_filter


@simple_filter
def package_name(v) -> str:
    """Return the package name (without namespace)."""
    return v.split(".")[1]


@simple_filter
def package_namespace(v) -> str:
    """Return the package namespace."""
    return v.split(".")[0]


@simple_filter
def pascal_case(package_name: str) -> str:
    """Return the package name as a string in the PascalCase format ."""
    parts = [name.title() for name in package_name.split("_")]
    return "".join(parts)
