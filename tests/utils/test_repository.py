from cookieplone import _types as t
from cookieplone import repository
from cookieplone.exceptions import RepositoryException
from cookieplone.exceptions import VersionTooOldException
from git import Repo
from pathlib import Path

import json
import pytest


TEMPLATE_PARAMS = [
    (
        "project",
        "A Plone Project",
        "Create a new Plone project with backend and frontend components",
        "templates/projects/monorepo",
    ),
    (
        "project_classic",
        "A Plone Classic Project",
        "Create a new Plone Classic project",
        "templates/projects/classic",
    ),
    (
        "backend_addon",
        "Backend Add-on for Plone",
        "Create a new Python package to be used with Plone",
        "templates/addons/backend",
    ),
    (
        "frontend_addon",
        "Frontend Add-on for Plone",
        "Create a new Node package to be used with Volto",
        "templates/addons/frontend",
    ),
    (
        "distribution",
        "A Plone and Volto distribution",
        "Create a new Distribution with Plone and Volto",
        "templates/distributions/monorepo",
    ),
]


class TestGetRepositoryConfigLegacy:
    """Tests for get_repository_config with legacy cookiecutter.json."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_sub_folder").resolve()

    def test_returns_dict(self, project_source):
        result = repository.get_repository_config(project_source)
        assert isinstance(result, dict)

    def test_has_templates(self, project_source):
        result = repository.get_repository_config(project_source)
        assert "templates" in result

    def test_no_config_file_raises(self, tmp_path):
        with pytest.raises(RuntimeError, match="No configuration file found"):
            repository.get_repository_config(tmp_path)


class TestGetRepositoryConfigNew:
    """Tests for get_repository_config with cookieplone-config.json."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_repo_config").resolve()

    def test_returns_dict(self, project_source):
        result = repository.get_repository_config(project_source)
        assert isinstance(result, dict)

    def test_has_templates(self, project_source):
        result = repository.get_repository_config(project_source)
        assert "templates" in result

    def test_has_groups(self, project_source):
        result = repository.get_repository_config(project_source)
        assert "groups" in result

    def test_has_config_versions(self, project_source):
        result = repository.get_repository_config(project_source)
        assert result["config"]["versions"]["gha_version_checkout"] == "v6"

    def test_prefers_new_format_over_legacy(self, tmp_path):
        """When both files exist, cookieplone-config.json wins."""
        legacy = {"templates": {"t": {"path": ".", "title": "T", "description": "D"}}}
        new = {
            "version": "1.0",
            "title": "New",
            "groups": {
                "g": {
                    "title": "G",
                    "description": "G",
                    "templates": ["t"],
                }
            },
            "templates": {"t": {"path": ".", "title": "T New", "description": "D"}},
        }
        (tmp_path / "cookiecutter.json").write_text(json.dumps(legacy))
        (tmp_path / "cookieplone-config.json").write_text(json.dumps(new))
        result = repository.get_repository_config(tmp_path)
        assert result["templates"]["t"]["title"] == "T New"

    def test_invalid_config_raises(self, tmp_path):
        """An invalid cookieplone-config.json raises RuntimeError."""
        bad = {"version": "1.0"}  # missing title, templates
        (tmp_path / "cookieplone-config.json").write_text(json.dumps(bad))
        with pytest.raises(RuntimeError, match=r"Invalid cookieplone-config\.json"):
            repository.get_repository_config(tmp_path)


class TestGetRepositoryConfigVersions:
    """Tests for config.versions extraction from cookieplone-config.json."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_repo_config").resolve()

    def test_config_versions_present(self, project_source):
        result = repository.get_repository_config(project_source)
        versions = result.get("config", {}).get("versions", {})
        assert versions == {"gha_version_checkout": "v6"}

    def test_legacy_config_has_no_versions(self, resources_folder):
        project_source = (resources_folder / "templates_sub_folder").resolve()
        result = repository.get_repository_config(project_source)
        versions = result.get("config", {}).get("versions", {})
        assert versions == {}


class TestGetTemplateOptionsLegacy:
    """Tests for get_template_options with legacy cookiecutter.json."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_sub_folder").resolve()

    @pytest.mark.parametrize("template_name,title,description,path", TEMPLATE_PARAMS)
    def test_get_template_options(
        self,
        project_source,
        template_name: str,
        title: str,
        description: str,
        path: str,
    ):
        results = repository.get_template_options(project_source)
        assert isinstance(results, dict)
        template = results[template_name]
        assert isinstance(template, t.CookieploneTemplate)
        assert template.title == title
        assert template.description == description
        assert isinstance(template.path, Path)
        assert f"{template.path}" == path

    @pytest.mark.parametrize(
        "all_,total_templates",
        [
            (False, 5),
            (True, 6),
        ],
    )
    def test_filter_hidden(self, project_source, all_: bool, total_templates: int):
        results = repository.get_template_options(project_source, all_)
        assert isinstance(results, dict)
        assert len(results) == total_templates


class TestGetTemplateOptionsNew:
    """Tests for get_template_options with cookieplone-config.json."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_repo_config").resolve()

    @pytest.mark.parametrize("template_name,title,description,path", TEMPLATE_PARAMS)
    def test_get_template_options(
        self,
        project_source,
        template_name: str,
        title: str,
        description: str,
        path: str,
    ):
        results = repository.get_template_options(project_source)
        assert isinstance(results, dict)
        template = results[template_name]
        assert isinstance(template, t.CookieploneTemplate)
        assert template.title == title
        assert template.description == description
        assert isinstance(template.path, Path)
        assert f"{template.path}" == path

    @pytest.mark.parametrize(
        "all_,total_templates",
        [
            (False, 5),
            (True, 6),
        ],
    )
    def test_filter_hidden(self, project_source, all_: bool, total_templates: int):
        results = repository.get_template_options(project_source, all_)
        assert isinstance(results, dict)
        assert len(results) == total_templates


class TestGetTemplateGroupsNew:
    """Tests for get_template_groups with cookieplone-config.json."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_repo_config").resolve()

    def test_returns_dict(self, project_source):
        result = repository.get_template_groups(project_source)
        assert isinstance(result, dict)

    def test_visible_groups_count(self, project_source):
        result = repository.get_template_groups(project_source, all_=False)
        assert len(result) == 3

    def test_all_groups_count(self, project_source):
        result = repository.get_template_groups(project_source, all_=True)
        assert len(result) == 4

    @pytest.mark.parametrize(
        "group_id,title,num_templates",
        [
            ("projects", "Projects", 2),
            ("addons", "Add-ons", 2),
            ("distributions", "Distributions", 1),
        ],
    )
    def test_visible_group_contents(
        self, project_source, group_id, title, num_templates
    ):
        result = repository.get_template_groups(project_source, all_=False)
        group = result[group_id]
        assert group.title == title
        assert len(group.templates) == num_templates

    def test_hidden_group_excluded_by_default(self, project_source):
        result = repository.get_template_groups(project_source, all_=False)
        assert "sub" not in result

    def test_hidden_group_included_with_all(self, project_source):
        result = repository.get_template_groups(project_source, all_=True)
        assert "sub" in result

    def test_group_templates_are_cookieplone_templates(self, project_source):
        result = repository.get_template_groups(project_source)
        for group in result.values():
            for tmpl in group.templates.values():
                assert isinstance(tmpl, t.CookieploneTemplate)


class TestGetTemplateGroupsLegacy:
    """Tests for get_template_groups with legacy cookiecutter.json (no groups)."""

    @pytest.fixture(scope="class")
    @classmethod
    def project_source(cls, resources_folder) -> Path:
        return (resources_folder / "templates_sub_folder").resolve()

    def test_returns_none(self, project_source):
        result = repository.get_template_groups(project_source)
        assert result is None


class TestRepositoryHasConfig:
    """Tests for _repository_has_config."""

    def test_with_legacy_config(self, resources_folder):
        path = resources_folder / "templates_sub_folder"
        assert repository._repository_has_config(path) is True

    def test_with_new_config(self, resources_folder):
        path = resources_folder / "templates_repo_config"
        assert repository._repository_has_config(path) is True

    def test_empty_dir(self, tmp_path):
        assert repository._repository_has_config(tmp_path) is False

    def test_nonexistent_dir(self, tmp_path):
        assert repository._repository_has_config(tmp_path / "nope") is False


class TestCheckoutFallbackTag:
    """Tests for checkout_fallback_tag."""

    @pytest.fixture
    def make_clone(self, tmp_path, resources_folder):
        """Clone a repository whose ``main`` branch has the legacy layout.

        On ``next``, ``cookiecutter.json`` is replaced by the
        ``cookieplone-config.json`` of ``templates_repo_config``, with
        *config_section* merged into its ``config`` block.  With
        ``with_config=False``, ``next`` has no repository configuration.
        """
        source = resources_folder / "templates_repo_config" / "cookieplone-config.json"
        source_config = json.loads(source.read_text())

        def func(with_config: bool = True, config_section: dict | None = None) -> Path:
            origin_dir = tmp_path / "origin"
            origin_dir.mkdir()
            origin = Repo.init(origin_dir, initial_branch="main")
            (origin_dir / "cookiecutter.json").write_text(json.dumps({"templates": {}}))
            origin.index.add(["cookiecutter.json"])
            origin.index.commit("Legacy layout")

            origin.git.checkout("-b", "next")
            origin.index.remove(["cookiecutter.json"], working_tree=True)
            (origin_dir / "README.md").write_text("Templates\n")
            origin.index.add(["README.md"])
            if with_config:
                config = dict(source_config)
                config["config"] = {
                    **config.get("config", {}),
                    **(config_section or {}),
                }
                (origin_dir / "cookieplone-config.json").write_text(json.dumps(config))
                origin.index.add(["cookieplone-config.json"])
            origin.index.commit("New layout")
            origin.git.checkout("main")

            clone_dir = tmp_path / "clone"
            Repo.clone_from(origin_dir, clone_dir)
            return clone_dir

        return func

    def test_checks_out_tag(self, make_clone):
        """The clone ends up on a local branch for the remote ``next``."""
        clone_dir = make_clone()
        result = repository.checkout_fallback_tag(clone_dir, "next")
        assert result == clone_dir.resolve()
        assert Repo(result).active_branch.name == "next"
        assert (result / "cookieplone-config.json").exists()

    def test_replaces_cached_config(self, make_clone):
        """The configuration cached for the previous checkout is discarded."""
        clone_dir = make_clone()
        assert "groups" not in repository.get_repository_config(clone_dir)
        repository.checkout_fallback_tag(clone_dir, "next")
        assert "groups" in repository.get_repository_config(clone_dir)

    def test_unknown_tag_raises(self, make_clone):
        """A tag missing from the clone surfaces as a RepositoryException."""
        clone_dir = make_clone()
        with pytest.raises(RepositoryException, match="Failed to check out"):
            repository.checkout_fallback_tag(clone_dir, "does-not-exist")

    def test_tag_without_config_raises(self, make_clone):
        """A tag without ``cookieplone-config.json`` is rejected."""
        clone_dir = make_clone(with_config=False)
        with pytest.raises(RepositoryException, match="not found"):
            repository.checkout_fallback_tag(clone_dir, "next")

    def test_min_version_checked(self, make_clone):
        """The ``min_version`` of the configuration at the new tag is enforced."""
        clone_dir = make_clone(config_section={"min_version": "999.0.0"})
        with pytest.raises(VersionTooOldException):
            repository.checkout_fallback_tag(clone_dir, "next")
