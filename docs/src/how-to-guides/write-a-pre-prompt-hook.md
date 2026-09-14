---
myst:
  html_meta:
    "description": "How to write a pre_prompt hook for a Cookieplone template that runs before the user is prompted."
    "property=og:description": "How to write a pre_prompt hook for a Cookieplone template that runs before the user is prompted."
    "property=og:title": "Write a pre-prompt hook"
    "keywords": "Cookieplone, pre_prompt hook, hooks, template, environment check"
---

# Write a pre-prompt hook

A `pre_prompt` hook runs before the interactive prompts are shown to the user.
Use it to check preconditions—for example, required system tools, network access, or minimum software versions.
If the hook raises an exception or exits with a non-zero status, Cookieplone aborts cleanly before asking any questions.

## Create the hook file

Inside your template directory, create a `hooks/` directory and add `pre_prompt.py`:

```
my-template/
└── templates/
    └── myproject/
        ├── cookieplone.json
        ├── hooks/
        │   └── pre_prompt.py
        └── {{cookiecutter.project_slug}}/
            └── ...
```

## Check for a required tool

```python
# hooks/pre_prompt.py
import shutil
import sys


def check_git():
    if shutil.which("git") is None:
        print("ERROR: git is required but not found on PATH.")
        sys.exit(1)


if __name__ == "__main__":
    check_git()
```

Cookieplone runs this script with the Python interpreter that runs Cookieplone itself, in a temporary copy of the template directory.
A non-zero exit code makes Cookieplone print the hook's output, followed by:

```text
Sanity checks failed.
Please review the errors above and try again.
```

Cookieplone then exits without asking any question.

## Check a minimum Python version

The hook runs with the interpreter that runs Cookieplone, so `sys.version_info` describes that interpreter, not a Python the generated project may use later:

```python
# hooks/pre_prompt.py
import sys

MINIMUM_PYTHON = (3, 10)

if sys.version_info < MINIMUM_PYTHON:
    print(
        f"ERROR: Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} or later is required. "
        f"You are running {sys.version}."
    )
    sys.exit(1)
```

## Raise a clean failure

Calling `sys.exit(1)` produces a clean exit with a message.
Do not raise unhandled exceptions; they produce a noisy traceback that obscures the real reason for the failure.

## When `pre_prompt` hooks run

The `pre_prompt` hook runs after the template repository is resolved and cloned, but before the interactive wizard starts.
It does not receive the user's answers because none have been collected yet.
For the same reason, Cookieplone doesn't render it with Jinja2: an expression such as `{{ cookiecutter.project_slug }}` in the script stays as written.
It also runs with `--no-input`, and on every re-run over an existing project.

See {doc}`/concepts/hooks` for the other hooks and how failures are handled.

## Related pages

- {doc}`/concepts/how-cookieplone-works`: the full generation pipeline including hook execution order.
- {doc}`/how-to-guides/debug-a-failed-generation`: debug hook failures.
