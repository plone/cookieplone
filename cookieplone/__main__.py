# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
"""Allow cookieplone to be executable through `python -m cookieplone`."""

from cookieplone.cli import main

if __name__ == "__main__":  # pragma: no cover
    main(prog_name="cookiecutter")
