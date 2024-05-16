import pytest

from cookieplone.utils import plone


@pytest.mark.parametrize(
    "package",
    [
        "plone.app.caching",
        "plone.app.dexterity",
        "plone.classicui",
    ],
)
def test_add_package_dependency_to_zcml(read_data_file, package: str):
    src_xml = read_data_file("plone/dependencies.zcml")
    func = plone.add_dependency_to_zcml
    assert package not in src_xml
    zcml_data = func(package, src_xml)
    assert f"""<include package="{package}"/>""" in zcml_data


@pytest.mark.parametrize(
    "profile",
    [
        "plone.app.caching:default",
        "plone.volto:default",
    ],
)
def test_add_dependency_profile_to_metadata(read_data_file, profile: str):
    src_xml = read_data_file("plone/metadata.xml")
    func = plone.add_dependency_profile_to_metadata
    assert profile not in src_xml
    xml_data = func(profile, src_xml)
    assert f"""<dependency>profile-{profile}</dependency>""" in xml_data
