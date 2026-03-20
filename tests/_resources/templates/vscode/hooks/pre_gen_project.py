"""Pre generation hook."""

from collections import OrderedDict
from pathlib import Path

output_path = Path().resolve()

context: OrderedDict = {{cookiecutter}}


def main():
    """Validate context."""
    pass


if __name__ == "__main__":
    main()
