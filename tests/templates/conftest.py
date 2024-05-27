import shutil

import pytest


@pytest.fixture
def project_folder(pytester, project_source):
    """Create fake cookiecutter project."""
    dest_path = pytester._path / "templates"
    if dest_path.exists():
        shutil.rmtree(dest_path, True)
    shutil.copytree(project_source, dest_path)
    return dest_path


@pytest.fixture
def testdir(pytester, project_folder):
    # create a temporary conftest.py file
    pytester.makeconftest(
        f"""
        from pathlib import Path
        import pytest

        # pytest_plugins = ["cookieplone.templates.fixtures"]

        @pytest.fixture(scope="session")
        def template_repository_root() -> Path:
            return Path("{project_folder}") / "project"
        """
    )
    return pytester
