"""Tests for _annotate_data."""

from cookieplone.generator.main import _annotate_data


def test_sets_template(run_config, repository_info):
    """_annotate_data sets _template to repo_dir."""
    data: dict = {"title": "Test"}
    _annotate_data(data, run_config, repository_info)
    assert data["_template"] == str(repository_info.repo_dir)


def test_sets_cookieplone_repository_path(run_config, repository_info):
    """_annotate_data sets __cookieplone_repository_path."""
    data: dict = {"title": "Test"}
    _annotate_data(data, run_config, repository_info)
    assert data["__cookieplone_repository_path"] == str(repository_info.root_repo_dir)


def test_sets_output_dir(run_config, repository_info):
    """_annotate_data sets _output_dir to resolved output_dir."""
    data: dict = {"title": "Test"}
    _annotate_data(data, run_config, repository_info)
    assert data["_output_dir"] == str(run_config.output_dir.resolve())


def test_sets_repo_dir(run_config, repository_info):
    """_annotate_data sets _repo_dir."""
    data: dict = {"title": "Test"}
    _annotate_data(data, run_config, repository_info)
    assert data["_repo_dir"] == str(repository_info.repo_dir)


def test_sets_checkout(run_config, repository_info):
    """_annotate_data sets _checkout."""
    data: dict = {"title": "Test"}
    _annotate_data(data, run_config, repository_info)
    assert data["_checkout"] == repository_info.checkout


def test_mutates_dict_in_place(run_config, repository_info):
    """_annotate_data mutates the input dict and returns None."""
    data: dict = {"title": "Test"}
    result = _annotate_data(data, run_config, repository_info)
    assert result is None
    assert "_template" in data
