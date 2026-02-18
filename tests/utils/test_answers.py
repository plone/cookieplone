from collections import OrderedDict

import pytest

from cookieplone.utils import answers


@pytest.mark.parametrize(
    "key, expected",
    [
        ("title", True),
        ("description", True),
        ("_hidden", False),
        ("__folder_name", False),
        ("__generator_sha", True),
        ("__cookieplone_template", True),
        ("__generator_signature", True),
    ],
)
def test_remove_internal_keys(context: OrderedDict[str, str], key: str, expected: bool):
    result = answers.remove_internal_keys(context)
    assert (key in result) is expected
