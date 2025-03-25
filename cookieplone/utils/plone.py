from pathlib import Path

import xmltodict

from cookieplone.logger import logger
from cookieplone.utils import formatters


def add_dependency_profile_to_metadata(profile: str, raw_xml: str) -> str:
    """Inject a dependency into the metadata.xml file."""
    data = xmltodict.parse(raw_xml)
    if not data["metadata"].get("dependencies"):
        data["metadata"]["dependencies"] = {"dependency": []}
    elif "dependency" not in data["metadata"].get("dependencies", {}):
        data["metadata"]["dependencies"]["dependency"] = []
    elements = data["metadata"]["dependencies"]["dependency"]
    if isinstance(elements, str):
        elements = [elements]
    elements.append(f"profile-{profile}")
    data["metadata"]["dependencies"]["dependency"] = elements
    raw_xml = xmltodict.unparse(data, short_empty_elements=True, pretty=True)
    return raw_xml


def add_dependency_to_zcml(package: str, raw_xml: str) -> str:
    """Inject a dependency into the dependencies.zcml file."""
    data = xmltodict.parse(raw_xml, process_namespaces=False)
    if not data["configure"].get("include"):
        data["configure"]["include"] = []
    data["configure"]["include"].append({"@package": f"{package}"})
    raw_xml = xmltodict.unparse(data, short_empty_elements=True, pretty=True)
    return raw_xml


OLD_PY_FORMATTERS = (
    ("zpretty", formatters.run_zpretty),
    ("isort", formatters.run_isort),
    ("black", formatters.run_black),
)

NEW_PY_FORMATTERS = (
    ("zpretty", formatters.run_zpretty),
    ("ruff", formatters.run_ruff),
)


def format_python_codebase(path: Path):
    """Format a Python codebase after code generation."""
    # Ensure there is a pyproject.toml
    pyproject = path / "pyproject.toml"
    if not pyproject.exists():
        logger.info(f"Format codebase: No pyproject.toml found in {path}, stopping")
    use_ruff = "[tool.ruff]" in pyproject.read_text()
    formatters = NEW_PY_FORMATTERS if use_ruff else OLD_PY_FORMATTERS
    # Run formatters
    for cmd, func in formatters:
        logger.debug(f"Format codebase: Running {cmd}")
        func(path)


def create_namespace_packages(
    path: Path, package_name: str, style: str = "pkg_resources"
):
    """Create namespace packages to hold an existing package."""
    current = path.parent
    for namespace in package_name.split(".")[:-1]:
        current = current / namespace
        current.mkdir()
        if style == "pkg_resources":
            (current / "__init__.py").write_text(
                '__import__("pkg_resources").declare_namespace(__name__)\n'
            )
        elif style == "pkgutil":
            (current / "__init__.py").write_text(
                "from pkgutil import extend_path\n\n"
                "__path__ = extend_path(__path__, __name__)\n"
            )
        else:
            # PEP 420 implicit namespace; no file needed.
            pass
    path.rename(current / package_name.split(".")[-1])
