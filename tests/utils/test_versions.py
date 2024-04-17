import pytest

from cookieplone.utils import versions


@pytest.fixture
def generate_version():
    from packaging.version import Version

    def func(value: str | None):
        if value:
            version = Version(value)
            return version

    return func


@pytest.fixture
def volto_versions():
    versions = ["17.15.5", "16.31.4", "18.0.0-alpha.27"]
    return versions


@pytest.fixture
def plone_versions():
    versions = [
        "5.0rc1",
        "5.0rc2",
        "5.0rc3",
        "5.1.0",
        "5.1.1",
        "5.1.2",
        "5.1.3",
        "5.1.4",
        "5.1.5",
        "5.1.6",
        "5.1.7",
        "5.1a1",
        "5.1a2",
        "5.1b1",
        "5.1b2",
        "5.1b3",
        "5.1b4",
        "5.1rc1",
        "5.1rc2",
        "5.2.0",
        "5.2.1",
        "5.2.10",
        "5.2.11",
        "5.2.12",
        "5.2.13",
        "5.2.14",
        "5.2.2",
        "5.2.3",
        "5.2.4",
        "5.2.5",
        "5.2.6",
        "5.2.7",
        "5.2.8",
        "5.2.9",
        "5.2a1",
        "5.2a2",
        "5.2b1",
        "5.2rc1",
        "5.2rc2",
        "5.2rc3",
        "5.2rc4",
        "5.2rc5",
        "6.0.0",
        "6.0.0a1",
        "6.0.0a2",
        "6.0.0a3",
        "6.0.0a4",
        "6.0.0a5",
        "6.0.0a6",
        "6.0.0b1",
        "6.0.0b2",
        "6.0.0b3",
        "6.0.0rc1",
        "6.0.0rc2",
        "6.0.1",
        "6.0.10",
        "6.0.2",
        "6.0.3",
        "6.0.4",
        "6.0.5",
        "6.0.6",
        "6.0.7",
        "6.0.8",
        "6.0.9",
        "6.1.0a1",
        "6.1.0a2",
    ]
    return versions


@pytest.fixture
def mock_npm_packages(monkeypatch, volto_versions):
    def get_npm_package_versions(*args, **kwargs):
        return volto_versions

    monkeypatch.setattr(versions, "get_npm_package_versions", get_npm_package_versions)


@pytest.fixture
def mock_pypi_packages(monkeypatch, plone_versions):
    def get_pypi_package_versions(*args, **kwargs):
        return plone_versions

    monkeypatch.setattr(
        versions, "get_pypi_package_versions", get_pypi_package_versions
    )


@pytest.mark.parametrize(
    "version,min_version,max_version,allow_prerelease,expected",
    [
        ["6.1.0a1", None, None, True, True],
        ["6.1.0a1", None, None, False, False],
        ["6.0.0", "6", None, False, True],
        ["6.0.0", "6.0", None, False, True],
        ["6.0.0", "6.0.0a1", None, False, True],
        ["6.0.0", "6.0.0", None, False, True],
        ["5.2.34", "6.0.0", None, False, False],
        ["18.0.0-alpha.27", "18", None, False, False],
        ["18.0.0-alpha.27", "18", None, True, False],
        ["18.0.0-alpha.27", "17", None, False, False],
        ["18.0.0-alpha.27", "17", None, True, True],
        ["18.0.0-alpha.27", "17", "18", True, True],
        ["18.0.0-alpha.27", "17", "17.99", True, False],
    ],
)
def test_is_valid_version(
    generate_version,
    version: str,
    min_version: str,
    max_version: str,
    allow_prerelease: bool,
    expected: bool,
):
    func = versions.is_valid_version
    args = [generate_version(v) for v in (version, min_version, max_version)]
    assert func(*args, allow_prerelease) is expected


def test_get_npm_package_versions():
    func = versions.get_npm_package_versions
    result = func("@plone/volto")
    assert isinstance(result, list)
    assert isinstance(result[0], str)


def test_get_pypi_package_versions():
    func = versions.get_pypi_package_versions
    result = func("Plone")
    assert isinstance(result, list)
    assert isinstance(result[0], str)


@pytest.mark.parametrize(
    "min_version,max_version,allow_prerelease,expected",
    [
        [None, None, True, "18.0.0-alpha.27"],
        [None, None, False, "17.15.5"],
        ["17", None, False, "17.15.5"],
        ["17", "18", False, "17.15.5"],
        ["17", "18", True, "18.0.0-alpha.27"],
        ["17", "17.99", True, "17.15.5"],
    ],
)
def test_latest_version(
    volto_versions,
    min_version: str,
    max_version: str,
    allow_prerelease: bool,
    expected: str,
):
    func = versions.latest_version
    assert func(volto_versions, min_version, max_version, allow_prerelease) == expected


@pytest.mark.parametrize(
    "min_version,max_version,allow_prerelease,expected",
    [
        [None, None, True, "18.0.0-alpha.27"],
        [None, None, False, "17.15.5"],
        ["17", None, False, "17.15.5"],
        ["17", "18", False, "17.15.5"],
        ["17", "18", True, "18.0.0-alpha.27"],
        ["17", "17.99", True, "17.15.5"],
    ],
)
def test_latest_volto(
    mock_npm_packages,
    min_version: str,
    max_version: str,
    allow_prerelease: bool,
    expected: str,
):
    func = versions.latest_volto
    assert func(min_version, max_version, allow_prerelease) == expected


@pytest.mark.parametrize(
    "min_version,max_version,allow_prerelease,expected",
    [
        [None, None, False, "6.0.10"],
        [None, None, True, "6.1.0a2"],
        [None, "5.99", False, "5.2.14"],
        ["5", "5.2", False, "5.1.7"],
        ["5", "6", False, "5.2.14"],
    ],
)
def test_latest_plone(
    mock_pypi_packages,
    min_version: str,
    max_version: str,
    allow_prerelease: bool,
    expected: str,
):
    func = versions.latest_plone
    assert func(min_version, max_version, allow_prerelease) == expected
