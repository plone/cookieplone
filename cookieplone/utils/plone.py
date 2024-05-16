import xmltodict


def add_dependency_profile_to_metadata(profile: str, raw_xml: str) -> str:
    """Inject a dependency into the metadata.xml file."""
    data = xmltodict.parse(raw_xml)
    if not data["metadata"].get("dependencies"):
        data["metadata"]["dependencies"] = []
    data["metadata"]["dependencies"].append({"dependency": f"profile-{profile}"})
    raw_xml = xmltodict.unparse(data, short_empty_elements=True, pretty=True)
    return raw_xml


def add_dependency_to_zcml(package: str, raw_xml: str) -> str:
    """Inject a dependency into the dependencies.zcml file."""
    data = xmltodict.parse(raw_xml, process_namespaces=False)
    if "include" not in data["configure"]:
        data["configure"]["include"] = []
    data["configure"]["include"].append({"@package": f"{package}"})
    raw_xml = xmltodict.unparse(data, short_empty_elements=True, pretty=True)
    return raw_xml
