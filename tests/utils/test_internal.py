import re
import sys
from pathlib import Path

from cookiecutter import __version__ as __cookiecutter_version__

from cookieplone import __version__
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


def test_signature_md_without_commit(no_repo):
    result = internal.signature_md(no_repo)
    assert isinstance(result, str)
    assert result.startswith(f"Generated using [Cookieplone ({__version__})]")
    assert "[cookiecutter-plone]" in result


def test_signature_md_with_commit(tmp_repo):
    result = internal.signature_md(tmp_repo)
    assert isinstance(result, str)
    assert result.startswith(f"Generated using [Cookieplone ({__version__})]")
    assert re.search(r"\[cookiecutter-plone \([a-f0-9]{7}\)]\([^\)]*\)", result)
