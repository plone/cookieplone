import re
import sys
from pathlib import Path

import pytest
from cookiecutter import __version__ as __cookiecutter_version__

from cookieplone import __version__, settings
from cookieplone.utils import internal


def test_version_info():
    result = internal.version_info()
    location = Path(__file__).parent.parent.parent / "cookieplone"
    expected = [
        f"Cookieplone {__version__} from {location} ",
        f"(Cookiecutter {__cookiecutter_version__}, ",
        f"Python {sys.version})",
    ]
    for entry in expected:
        assert entry in result


@pytest.mark.parametrize(
    "panel_id,panel_title",
    [
        ["cookieplone", "Installation :zap:"],
        ["repository", "Repository :link:"],
        ["cookiecutter", "Cookiecutter :cookie:"],
        ["python", "Python :snake:"],
    ],
)
def test_cookieplone_info(panel_id: str, panel_title: str):
    result = internal.cookieplone_info(settings.REPO_DEFAULT)
    assert isinstance(result, dict)
    assert result["title"] == "cookieplone"
    assert result["subtitle"] == internal.SIGNATURE
    panels = result["panels"]
    assert isinstance(panels, dict)
    panel = panels[panel_id]
    assert isinstance(panel, dict)
    assert panel["title"] == panel_title


def test_signature_md_without_commit(no_repo):
    result = internal.signature_md(no_repo)
    assert isinstance(result, str)
    assert result.startswith(f"Generated using [Cookieplone ({__version__})]")
    assert "[cookieplone-templates]" in result


def test_signature_md_with_commit(tmp_repo):
    result = internal.signature_md(tmp_repo)
    assert isinstance(result, str)
    assert result.startswith(f"Generated using [Cookieplone ({__version__})]")
    assert re.search(r"\[cookieplone-templates \([a-f0-9]{7}\)]\([^\)]*\)", result)
