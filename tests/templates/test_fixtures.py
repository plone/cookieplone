import pytest


def test_fixture_variable_pattern(testdir):
    """Test variable_pattern fixture."""
    testdir.makepyfile(
        """
        import re

        def test_fixture(variable_pattern):
            assert isinstance(variable_pattern, re.Pattern)
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "value,expected",
    [
        ["{{cookiecutter.title}}", "title"],
        ["{{ cookiecutter.title}}", "title"],
        ["{{ cookiecutter.title }}", "title"],
        [
            "{%- if cookiecutter.__devops_traefik_local_include_ui == 'yes' %}",
            "__devops_traefik_local_include_ui",
        ],
    ],
)
def test_fixture_find_variables(testdir, value: str, expected: str):
    """Test find_variables fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(find_variables):
            result = find_variables("{value}")
            assert isinstance(result, set)
            assert "{expected}" in result
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "value,expected",
    [
        ["title", True],
        ["__title", True],
        ["_internal", False],
        ["__prompts__", False],
    ],
)
def test_fixture_valid_key(testdir, value: str, expected: bool):
    """Test valid_key fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(valid_key):
            result = valid_key("{value}")
            assert result is {expected}
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_fixture_template_folder_name(testdir):
    """Test template_folder_name fixture."""
    expected = "{{ cookiecutter.__folder_name }}"
    testdir.makepyfile(
        f"""
        def test_fixture(template_folder_name):
            assert template_folder_name == "{expected}"
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize("key", ["title", "description", "check"])
def test_fixture_configuration_data(testdir, key: str):
    """Test configuration_data fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(configuration_data):
            assert isinstance(configuration_data, dict)
            assert "{key}" in configuration_data
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_fixture_sub_templates(testdir):
    """Test sub_templates fixture."""
    testdir.makepyfile(
        """
        from pathlib import Path

        def test_fixture(sub_templates):
            assert isinstance(sub_templates, list)
            assert len(sub_templates) == 1
            assert isinstance(sub_templates[0], Path)
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "key", ["title", "description", "check", "__profile_language", "double_check"]
)
def test_fixture_project_variables(testdir, key: str):
    """Test project_variables fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(project_variables):
            assert isinstance(project_variables, set)
            assert "{key}" in project_variables
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "key", ["__cookieplone_repository_path", "__cookieplone_template"]
)
def test_fixture_variables_required(testdir, key: str):
    """Test variables_required fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(variables_required):
            assert isinstance(variables_required, set)
            assert "{key}" in variables_required
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize("key", ["double_check"])
def test_fixture_variables_missing(testdir, key: str):
    """Test variables_missing fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(variables_missing):
            assert isinstance(variables_missing, list)
            assert "{key}" in variables_missing
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize("key", ["__cookieplone_subtemplates"])
def test_fixture_variables_not_used(testdir, key: str):
    """Test variables_not_used fixture."""
    testdir.makepyfile(
        f"""
        def test_fixture(variables_not_used):
            assert isinstance(variables_not_used, list)
            assert "{key}" in variables_not_used
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
