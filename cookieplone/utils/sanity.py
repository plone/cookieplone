# SPDX-FileCopyrightText: 2024-present Plone Foundation <board@plone.org>
#
# SPDX-License-Identifier: MIT
from cookieplone import data


def run_sanity_checks(checks: list[data.SanityCheck]) -> data.SanityCheckResults:
    """Run sanity checks."""
    global_status = True
    results = []
    for check in checks:
        status = False
        name = check.name
        func = check.func
        args = check.args
        level = check.level
        message = func(*args)
        if not message:
            status = True
            message = "✓"
        elif level == "warning":
            status = True
        global_status = global_status and status
        results.append(data.SanityCheckResult(name, status, message))
    global_message = (
        f"Ran {len(checks)} checks and they {'passed' if global_status else 'failed'}."
    )
    return data.SanityCheckResults(
        status=global_status, message=global_message, checks=results
    )
