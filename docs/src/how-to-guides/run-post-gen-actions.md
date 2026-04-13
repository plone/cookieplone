---
myst:
  html_meta:
    "description": "How to use run_post_gen_actions() and built-in handlers to streamline post-generation hooks."
    "property=og:description": "How to use run_post_gen_actions() and built-in handlers to streamline post-generation hooks."
    "property=og:title": "Run post-generation actions"
    "keywords": "Cookieplone, post_gen_project, run_post_gen_actions, handlers, git, namespace packages"
---

# Run post-generation actions

This guide shows how to replace hand-rolled action loops in `post_gen_project.py` with {py:func}`cookieplone.utils.post_gen.run_post_gen_actions` and its built-in handlers.

## The problem

Every template's post-generation hook tends to repeat the same pattern:

```python
# Old pattern, duplicated across templates.
actions = [
    [handle_backend_cleanup, "Backend final cleanup", True],
    [handle_devops_ansible, "Remove Ansible files", not feature_devops_ansible],
    [handle_git_initialization, "Initialize Git repository", initialize_git],
]
for func, title, enabled in actions:
    if not int(enabled):
        continue
    console.print(f" -> {title}")
    func(deepcopy(context), output_dir)
```

`run_post_gen_actions()` replaces this boilerplate with a single call and ships ready-made handlers for the most common tasks.

## Prerequisites

- Your template has a `hooks/post_gen_project.py` file.
- You have already handled sub-template generation (see {doc}`call-subtemplates-from-a-hook`) and now want to run final cleanup actions.

## Step 1: Import the helper and handlers

```python
from collections import OrderedDict
from pathlib import Path

from cookieplone.utils.post_gen import (
    run_post_gen_actions,
    create_namespace_packages,
    initialize_git_repository,
    move_files,
    remove_files_by_key,
    run_make_format,
)

context: OrderedDict = {{cookiecutter}}
```

## Step 2: Define your action list

Each action is a dictionary with three keys:

| Key | Type | Description |
|-----|------|-------------|
| `handler` | `Callable[[OrderedDict, Path], None]` | The function to run. |
| `title` | `str` | Label printed to the console. |
| `enabled` | `bool` | When false (or `0`), the action is skipped with an "Ignoring" message. |

```python
POST_GEN_TO_REMOVE = {
    "devops-ansible": ["devops/ansible"],
    "devops-gha": [".github/workflows/deploy.yml"],
}

initialize_git = context.get("initialize_git", "1")

actions = [
    {
        "handler": create_namespace_packages,
        "title": "Backend final cleanup",
        "enabled": True,
    },
    {
        "handler": remove_files_by_key(POST_GEN_TO_REMOVE, "devops-ansible"),
        "title": "Remove Ansible files",
        "enabled": not int(context.get("feature_devops_ansible", "0")),
    },
    {
        "handler": move_files([("docs/.readthedocs.yaml", ".readthedocs.yml")]),
        "title": "Organize documentation files",
        "enabled": int(context.get("feature_documentation", "0")),
    },
    {
        "handler": run_make_format("format", "backend"),
        "title": "Format backend code",
        "enabled": True,
    },
    {
        "handler": initialize_git_repository,
        "title": "Initialize Git repository",
        "enabled": initialize_git,
    },
]
```

## Step 3: Invoke from `main()`

```python
def main():
    output_dir = Path.cwd()

    # Sub-template generation (if any) goes here first.
    # ...

    # Post-generation actions
    run_post_gen_actions(context, output_dir, actions)


if __name__ == "__main__":
    main()
```

Each enabled action receives a **deep copy** of the context, so handlers can safely mutate it without affecting subsequent actions.

## Built-in handlers

### `initialize_git_repository`

Initializes a git repository in the output directory and stages all files.
Wraps {py:func}`cookieplone.utils.git.initialize_repository` with a second `git add` to capture files created by earlier actions.

```python
{"handler": initialize_git_repository, "title": "Initialize Git", "enabled": True}
```

### `create_namespace_packages`

Creates Python namespace package directories.
Reads `python_package_name` and `namespace_style` (default `"native"`) from the context.
Skips if the package name has no dots.

```python
{"handler": create_namespace_packages, "title": "Namespace packages", "enabled": True}
```

### `remove_files_by_key(to_remove, key)`

Factory that returns a handler removing files listed under the given key in the removal dict.

```python
TO_REMOVE = {
    "devops-ansible": ["devops/ansible", "devops/ansible.cfg"],
    "devops-gha": [".github/workflows/deploy.yml"],
}
{"handler": remove_files_by_key(TO_REMOVE, "devops-ansible"), "title": "Remove Ansible", "enabled": True}
```

### `move_files(pairs)`

Factory that returns a handler renaming files within the output directory.
Creates destination parent directories as needed.

```python
{"handler": move_files([("docs/.readthedocs.yaml", ".readthedocs.yml")]), "title": "Move docs", "enabled": True}
```

### `run_make_format(make_target, folder)`

Factory that returns a handler running `make <target>` in a subfolder.
Defaults to `make format` in the output directory.
Skips silently if no `Makefile` is found.

```python
{"handler": run_make_format("format", "backend"), "title": "Format backend", "enabled": True}
```

## Writing custom handlers

Any function matching the `PostGenHandler` signature works:

```python
from collections import OrderedDict
from pathlib import Path


def my_custom_action(context: OrderedDict, output_dir: Path) -> None:
    """Do something template-specific."""
    config_path = output_dir / "config.yaml"
    if config_path.exists():
        # Template-specific logic here
        ...
```

Then use it in the actions list:

```python
{"handler": my_custom_action, "title": "Custom config setup", "enabled": True}
```

## Related pages

- {doc}`call-subtemplates-from-a-hook`: orchestrating sub-template generation before post-gen actions.
- {doc}`write-a-pre-prompt-hook`: running validation *before* the wizard.
- {doc}`/concepts/how-cookieplone-works`: the full generation pipeline.
