import pytest


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
            return Path("{project_folder}") / "vscode"

        @pytest.fixture(scope="module")
        def template_path(template_repository_root) -> str:
            return str(template_repository_root)

        """
    )
    return pytester


def test_fixture_template_folder_name(testdir):
    """Test template_folder_name fixture."""
    expected = ".vscode"
    testdir.makepyfile(
        f"""
            from pathlib import Path
            import pytest

            @pytest.fixture(scope="session")
            def cookieplone_root():
                return Path("{testdir.path}")
        """
        """
            @pytest.fixture(scope="session")
            def context(annotate_context, cookieplone_root) -> dict:
                return annotate_context(
                    {
                        "backend_path": "/backend",
                        "frontend_path": "/frontend",
                        "ansible_path": "/devops/ansible",
                    },
                    cookieplone_root,
                    "ide_vscode",
                )

        """
        f"""
            def test_creation(cookies, template_path, context: dict):
                result = cookies.bake(extra_context=context, template=template_path)
                assert result.exit_code == 0
                assert result.exception is None
                assert result.project_path.name == "{expected}"
                assert result.project_path.is_dir()
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
