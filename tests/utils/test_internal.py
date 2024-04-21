import sys
from pathlib import Path

import pytest

from cookiecutter import __version__ as __cookiecutter_version__
from cookieplone import __version__
from cookieplone.utils import internal


def test_version_info():
    result = internal.version_info()
    location = Path(__file__).parent.parent.parent / "cookieplone"
    expected = (
        f"Cookieplone {__version__} from {location} "
        f"(Cookiecutter {__cookiecutter_version__}, "
        f"Python {sys.version})"
    )
    assert result == expected
