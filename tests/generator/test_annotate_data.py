"""Tests for _annotate_data."""

from cookieplone.config.state import CookieploneState
from cookieplone.generator.main import _annotate_data


def test_sets_template(state, run_config, repository_info):
    """_annotate_data sets _template to repo_dir."""
    data: dict = {"title": "Test"}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_template"] == str(repository_info.repo_dir)


def test_sets_cookieplone_repository_path(state, run_config, repository_info):
    """_annotate_data sets __cookieplone_repository_path."""
    data: dict = {"title": "Test"}
    _annotate_data(data, state, run_config, repository_info)
    assert data["__cookieplone_repository_path"] == str(repository_info.root_repo_dir)


def test_sets_output_dir(state, run_config, repository_info):
    """_annotate_data sets _output_dir to resolved output_dir."""
    data: dict = {"title": "Test"}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_output_dir"] == str(run_config.output_dir.resolve())


def test_sets_repo_dir(state, run_config, repository_info):
    """_annotate_data sets _repo_dir."""
    data: dict = {"title": "Test"}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_repo_dir"] == str(repository_info.repo_dir)


def test_sets_checkout(state, run_config, repository_info):
    """_annotate_data sets _checkout."""
    data: dict = {"title": "Test"}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_checkout"] == repository_info.checkout


def test_mutates_dict_in_place(state, run_config, repository_info):
    """_annotate_data mutates the input dict and returns None."""
    data: dict = {"title": "Test"}
    result = _annotate_data(data, state, run_config, repository_info)
    assert result is None
    assert "_template" in data


def test_injects_extensions(run_config, repository_info):
    """_annotate_data injects _extensions when state has extensions."""
    state = CookieploneState(
        schema={"version": "2.0", "properties": {}},
        data={"cookiecutter": {}},
        extensions=["cookieplone.filters.latest_plone"],
    )
    data: dict = {}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_extensions"] == ["cookieplone.filters.latest_plone"]


def test_injects_no_render(run_config, repository_info):
    """_annotate_data injects _copy_without_render when state has no_render."""
    state = CookieploneState(
        schema={"version": "2.0", "properties": {}},
        data={"cookiecutter": {}},
        no_render=["*.png", "devops/etc"],
    )
    data: dict = {}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_copy_without_render"] == ["*.png", "devops/etc"]


def test_injects_subtemplates(run_config, repository_info):
    """_annotate_data injects __cookieplone_subtemplates as v1 tuples."""
    state = CookieploneState(
        schema={"version": "2.0", "properties": {}},
        data={"cookiecutter": {}},
        subtemplates=[
            {"id": "sub/backend", "title": "Backend", "enabled": "1"},
        ],
    )
    data: dict = {}
    _annotate_data(data, state, run_config, repository_info)
    assert data["__cookieplone_subtemplates"] == [["sub/backend", "Backend", "1"]]


def test_injects_empty_config_defaults(state, run_config, repository_info):
    """_annotate_data injects config keys with empty defaults when state has none."""
    data: dict = {}
    _annotate_data(data, state, run_config, repository_info)
    assert data["_extensions"] == []
    assert data["_copy_without_render"] == []
    assert data["__cookieplone_subtemplates"] == []
    assert data["__cookieplone_template"] == ""
