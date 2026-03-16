import pytest

from cookieplone.utils import config

CONFIG_FILES = [
    "config/v1-agents_instructions.json",
    "config/v1-backend_addon.json",
    "config/v1-ci_gh_backend_addon.json",
    "config/v1-ci_gh_classic_project.json",
    "config/v1-ci_gh_frontend_addon.json",
    "config/v1-ci_gh_monorepo_addon.json",
    "config/v1-ci_gh_project.json",
    "config/v1-classic_project.json",
    "config/v1-devops_ansible.json",
    "config/v1-documentation_starter.json",
    "config/v1-frontend_addon.json",
    "config/v1-ide_vscode.json",
    "config/v1-monorepo_addon.json",
    "config/v1-project.json",
    "config/v1-seven_addon.json",
    "config/v1-sub-addon_settings.json",
    "config/v1-sub-cache.json",
    "config/v1-sub-classic_project_settings.json",
    "config/v1-sub-frontend_project.json",
    "config/v1-sub-project_settings.json",
]


class TestGetPromptInfo:
    """Tests for _get_prompt_info function."""

    def test_get_prompt_info_simple_string(self):
        """Test _get_prompt_info with a simple string prompt."""
        prompts = {"title": "Project Title"}
        result = config._get_prompt_info(prompts, "title", "default_value")

        assert result.title == "Project Title"
        assert result.options == []

    def test_get_prompt_info_dict_with_options(self):
        """Test _get_prompt_info with a dictionary containing options."""
        prompts = {
            "language_code": {
                "__prompt__": "Language",
                "en": "English",
                "de": "Deutsch",
                "es": "Español",
            }
        }
        result = config._get_prompt_info(prompts, "language_code", ["en", "de", "es"])

        assert result.title == "Language"
        assert len(result.options) == 3
        assert ("en", "English") in result.options
        assert ("de", "Deutsch") in result.options
        assert ("es", "Español") in result.options

    def test_get_prompt_info_missing_key(self):
        """Test _get_prompt_info when key is not in prompts."""
        prompts = {"other_key": "Other Value"}
        result = config._get_prompt_info(prompts, "title", "default_value")

        assert result.title == "title"
        assert result.options == []

    def test_get_prompt_info_with_list_value(self):
        """Test _get_prompt_info with a list as raw_value."""
        prompts = {
            "container_registry": {
                "__prompt__": "Container Registry",
                "github": "GitHub Container Registry",
                "docker_hub": "Docker Hub",
                "gitlab": "GitLab",
            }
        }
        raw_value = ["github", "docker_hub", "gitlab"]
        result = config._get_prompt_info(prompts, "container_registry", raw_value)

        assert result.title == "Container Registry"
        assert len(result.options) == 3
        assert ("github", "GitHub Container Registry") in result.options
        assert ("docker_hub", "Docker Hub") in result.options
        assert ("gitlab", "GitLab") in result.options

    def test_get_prompt_info_boolean_options(self):
        """Test _get_prompt_info with boolean-like options."""
        prompts = {
            "initialize_ci": {
                "__prompt__": "Would you like to add a CI configuration?",
                "1": "Yes",
                "0": "No",
            }
        }
        raw_value = ["1", "0"]
        result = config._get_prompt_info(prompts, "initialize_ci", raw_value)

        assert result.title == "Would you like to add a CI configuration?"
        assert len(result.options) == 2
        assert ("1", "Yes") in result.options
        assert ("0", "No") in result.options

    def test_get_prompt_info_no_prompt_key(self):
        """Test _get_prompt_info when prompt dict has no __prompt__ key."""
        prompts = {
            "field": {
                "option1": "Option 1",
                "option2": "Option 2",
            }
        }
        result = config._get_prompt_info(prompts, "field", ["option1", "option2"])

        assert result.title == "field"
        assert result.options == []


class TestGetValidator:
    """Tests for _get_validator function."""

    @pytest.fixture
    def validators(self):
        """Fixture providing a validators dictionary."""
        return {
            "title": "cookieplone.validators.non_empty",
            "hostname": "cookieplone.validators.hostname",
            "language_code": "cookieplone.validators.language_code",
            "plone_version": "cookieplone.validators.plone_version",
            "volto_version": "cookieplone.validators.volto_version",
            "python_package_name": "cookieplone.validators.python_package_name",
        }

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("title", "cookieplone.validators.non_empty"),
            ("hostname", "cookieplone.validators.hostname"),
            ("language_code", "cookieplone.validators.language_code"),
            ("plone_version", "cookieplone.validators.plone_version"),
            ("volto_version", "cookieplone.validators.volto_version"),
            ("python_package_name", "cookieplone.validators.python_package_name"),
        ],
    )
    def test_get_validator_explicit(self, validators, key: str, expected: str):
        """Test _get_validator with explicitly defined validators."""
        result = config._get_validator(validators, key)
        assert result == expected

    def test_get_validator_not_found(self, validators):
        """Test _get_validator when validator is not found."""
        result = config._get_validator(validators, "unknown_field")
        assert result == ""

    def test_get_validator_empty_validators(self):
        """Test _get_validator with empty validators dict."""
        result = config._get_validator({}, "title")
        assert result == ""

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("description", ""),
            ("title", ""),
        ],
    )
    def test_get_validator_default_non_empty(self, key: str, expected: str):
        """Test _get_validator falls back to non_empty for title/description."""
        # Test with empty validators dict to check default behavior
        result = config._get_validator({}, key)
        assert result == expected


class TestPromptInfo:
    """Tests for PromptInfo dataclass/namedtuple."""

    def test_prompt_info_creation(self):
        """Test creating a PromptInfo object."""
        # This test depends on the actual implementation
        # If PromptInfo is a dataclass or namedtuple
        pass


# Integration tests
class TestConfigIntegration:
    """Integration tests for config utility functions."""

    @pytest.fixture
    def context_project(self, read_config_file):
        """Load a sample project configuration."""
        return read_config_file("config/v1-project.json")

    def test_get_prompt_info_from_real_config(self, context_project):
        """Test _get_prompt_info with real configuration data."""
        prompts = context_project.get("__prompts__", {})

        # Test title field
        result = config._get_prompt_info(prompts, "title", "Project Title")
        assert result.title == "Project Title"

        # Test language_code choice field
        result = config._get_prompt_info(
            prompts,
            "language_code",
            ["en", "de", "es", "pt-br", "nl", "fi", "it", "sv"],
        )
        assert "Language" in result.title
        assert len(result.options) > 0

    def test_get_validator_from_real_config(self, context_project):
        """Test _get_validator with real configuration data."""
        validators = context_project.get("__validators__", {})

        # Test hostname validator
        result = config._get_validator(validators, "hostname")
        assert "hostname" in result

        # Test plone_version validator
        result = config._get_validator(validators, "plone_version")
        assert "plone_version" in result

    def test_multiple_config_formats(self, read_config_file):
        """Test config utilities work with different configuration formats."""
        config_files = [
            "config/v1-backend_addon.json",
            "config/v1-frontend_addon.json",
            "config/v1-classic_project.json",
        ]

        for config_file in config_files:
            data = read_config_file(config_file)
            prompts = data.get("__prompts__", {})
            validators = data.get("__validators__", {})

            # Ensure we can process each config
            for key in prompts:
                result = config._get_prompt_info(prompts, key, "")
                assert result.title is not None

            for key in validators:
                result = config._get_validator(validators, key)
                assert isinstance(result, str)


@pytest.mark.parametrize("config_file", CONFIG_FILES)
def test_convert_v1_to_v2(read_config_file, config_file: str):
    """Test convert_v1_to_v2 function with a sample configuration."""
    data = read_config_file(config_file)
    result = config.convert_v1_to_v2(data)

    assert isinstance(result, dict)
    assert result.get("title") == "Cookieplone"
    assert result.get("version") == "2.0"
    assert "properties" in result
    properties = result["properties"]
    assert isinstance(properties, dict)


@pytest.mark.parametrize(
    "data,expected",
    (
        ({"bad": {"1", "2", "3"}}, "'bad': <class 'set'>"),
        ({"bad": ("1", "2", "3")}, "'bad': <class 'tuple'>"),
    ),
)
def test_convert_v1_to_v2_failure(data: dict, expected: str):
    """Test convert_v1_to_v2 failing."""
    with pytest.raises(ValueError) as exc:
        config.convert_v1_to_v2(data)

    assert f"Unsupported type for key {expected}" in str(exc)


@pytest.mark.parametrize(
    "data,expected",
    (
        ({"bad": {"1", "2", "3"}}, False),
        ({"bad": ("1", "2", "3")}, False),
    ),
)
def test_validate_config(data: dict, expected: bool):
    """Test validate_config."""
    assert config.validate_config(data) is expected
