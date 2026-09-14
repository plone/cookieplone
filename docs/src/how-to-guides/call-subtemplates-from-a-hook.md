---
myst:
  html_meta:
    "description": "How to orchestrate sub-template generation from a post-generation hook using run_subtemplates and custom handlers."
    "property=og:description": "How to orchestrate sub-template generation from a post-generation hook using run_subtemplates and custom handlers."
    "property=og:title": "Call sub-templates from a hook"
    "keywords": "Cookieplone, sub-templates, post_gen_project, run_subtemplates, handlers, monorepo"
---

# Call sub-templates from a hook

```{versionadded} 2.0.0
```

This guide shows how to drive sub-template generation from a top-level template's `post_gen_project.py`, using {py:func}`cookieplone.utils.subtemplates.run_subtemplates` and a dictionary of custom handlers.
It follows the `project` template of [`plone/cookieplone-templates`](https://github.com/plone/cookieplone-templates), in `templates/projects/monorepo`, which composes a full Plone project out of seven sub-templates: backend, frontend, documentation, cache, project settings, CI, and VS Code configuration.
The code samples are adapted from that template's hook.

## Prerequisites

- Your template's `cookieplone.json` lists the sub-templates under `config.subtemplates` (see {doc}`/concepts/subtemplates`).
- You know which sub-templates need custom handling, such as extra context, a specific output folder, or post-processing.

## Step 1: Import the helpers

At the top of `hooks/post_gen_project.py`:

```python
from collections import OrderedDict
from pathlib import Path

from cookieplone import generator
from cookieplone.utils import post_gen
from cookieplone.utils.subtemplates import run_subtemplates

context: OrderedDict = {{cookiecutter}}
versions: dict | OrderedDict = {{versions}}

TEMPLATES_FOLDER: str = "templates"
```

Cookieplone renders the hook with Jinja2 before running it.
`{{cookiecutter}}` becomes the answers, and `{{versions}}` becomes the version pins from `config.versions`.
The answers include `__cookieplone_subtemplates`: the entries of `config.subtemplates`, with `enabled` already rendered.

## Step 2: Write one handler per sub-template

A handler has the signature `(context: OrderedDict, output_dir: Path) -> Path`, and returns the directory that the sub-template generated.
`run_subtemplates()` passes each handler a deep copy of the context, so changing `context` in place is safe.

Handlers call {py:func}`cookieplone.generator.generate_subtemplate` with:

- the path of the sub-template, `templates/<id>`;
- the directory to generate in;
- the folder name for the sub-template's top-level directory;
- the context;
- optionally, a list of paths to remove from the generated folder, and the version pins as `global_versions`.

The sub-templates in `cookieplone-templates` name their top-level directory `{{ cookiecutter.__folder_name }}`, and `generate_subtemplate` sets `__folder_name` to the folder name you pass.

### Generate into a new folder

The backend add-on goes into a `backend` folder of the project, without the CI and documentation that a stand-alone add-on would have:

```python
BACKEND_ADDON_REMOVE: list[str] = [
    ".git",
]


def generate_addons_backend(context: OrderedDict, output_dir: Path) -> Path:
    """Run Plone Addon generator."""
    folder_name = "backend"
    # Headless
    feature_headless = bool(context.get("feature_headless", True))
    context["feature_headless"] = feature_headless
    context["initialize_ci"] = False
    context["initialize_documentation"] = False
    path = generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/add-ons/backend",
        output_dir,
        folder_name,
        context,
        BACKEND_ADDON_REMOVE,
        global_versions=versions,
    )
    return path
```

### Post-process the generated files

The frontend handler changes the generated files after generation, turning off the release automation that only a stand-alone add-on needs:

```python
import json

FRONTEND_ADDON_REMOVE: list[str] = []


def generate_addons_frontend(context: OrderedDict, output_dir: Path) -> Path:
    """Run volto generator."""
    folder_name = "frontend"
    # Handle packages inside an organization
    context = _fix_frontend_addon_name(context)
    frontend_addon_name = context["frontend_addon_name"]
    context["initialize_documentation"] = False
    context["initialize_ci"] = False
    path = generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/add-ons/frontend",
        output_dir,
        folder_name,
        context,
        FRONTEND_ADDON_REMOVE,
        global_versions=versions,
    )
    # Handle .release-it.json
    release_it_path = path / "packages" / frontend_addon_name / ".release-it.json"
    if release_it_path.is_file():
        data = json.loads(release_it_path.read_text())
        data["github"]["release"] = False
        data["plonePrePublish"]["publish"] = False
        data["npm"]["publish"] = False
        release_it_path.write_text(json.dumps(data, indent=2))
    return path
```

In the real hook, `_fix_frontend_addon_name` is a helper in the same file that handles scoped npm package names, and the handler also replaces the add-on's repository addresses with the project's.

### Generate with a smaller context

Some sub-templates need only a few values derived from the parent's answers.
The GitHub Actions sub-template gets a context of its own:

```python
def generate_ci_gh_project(context: OrderedDict, output_dir: Path) -> Path:
    """Generate GitHub CI."""
    feature_headless = bool(context.get("feature_headless", True))
    ci_context = OrderedDict({
        "feature_headless": feature_headless,
        "python_version": versions["backend_python"],
        "node_version": context.get("__node_version", ""),
        "has_cache": "1" if context["devops_cache"] else "0",
        "has_docs": "1" if context["initialize_documentation"] else "0",
        "has_deploy": "1" if context["devops_gha_deploy"] else "0",
        "__cookieplone_repository_path": context["__cookieplone_repository_path"],
    })
    return generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/ci/gh_project",
        output_dir,
        ".github",
        ci_context,
        global_versions=versions,
    )
```

The generated files land in `.github/` at the project root, because the handler passes `.github` as the folder name.
The smaller context keeps `__cookieplone_repository_path`, which `generate_subtemplate` uses to find the sub-template.

### Merge into the project folder

Some sub-templates add files to the project folder itself, without a folder of their own:

```python
def generate_sub_cache(context: OrderedDict, output_dir: Path) -> Path:
    """Add cache structure."""
    # Use the same base folder
    folder_name = output_dir.name
    parent_dir = output_dir.parent
    return generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/sub/cache",
        parent_dir,
        folder_name,
        context,
        global_versions=versions,
    )
```

Generating in the project's parent directory, with the project's name as folder name, makes the sub-template's top-level directory the project directory, so its files merge into the project.

## Step 3: Register the handlers

Collect the handlers in a module-level dictionary, keyed by the `id` of each entry in `config.subtemplates`:

```python
SUBTEMPLATE_HANDLERS = {
    "add-ons/backend": generate_addons_backend,
    "add-ons/frontend": generate_addons_frontend,
    "docs/starter": generate_docs_starter,
    "sub/cache": generate_sub_cache,
    "sub/project_settings": generate_sub_project_settings,
    "ci/gh_project": generate_ci_gh_project,
    "ide/vscode": generate_ide_vscode,
}
```

For an entry without a handler, `run_subtemplates()` generates `templates/<id>` in the project directory, with the project's name as folder name.
A sub-template whose top-level directory is `{{ cookiecutter.__folder_name }}` then lands in a nested folder: for a project in `my-project`, in `my-project/my-project/`.
Register a handler for every sub-template whose output location matters, as the `project` template does for all seven.

## Step 4: Call `run_subtemplates()` from `main()`

In the `main()` function of the hook, generate the sub-templates, then run the remaining post-generation actions:

```python
def main():
    """Final fixes."""
    output_dir = Path().cwd()
    run_subtemplates(
        context, output_dir, handlers=SUBTEMPLATE_HANDLERS, global_versions=versions
    )
    # Action handlers
    post_gen.run_post_gen_actions(context, output_dir, action_handlers(context))


if __name__ == "__main__":
    main()
```

`action_handlers(context)` is a function in the same hook that returns the list of post-generation actions, such as formatting code and initializing a git repository.
See {doc}`run-post-gen-actions`.

### Propagate version pins

The `global_versions` parameter passes the parent template's version pins (from {ref}`config.versions <repo-config>`) to the sub-templates, so their files can use `{{ versions.<key> }}`.
Pass the `versions` variable that Cookieplone renders into the hook, both to `run_subtemplates()` and to each `generate_subtemplate()` call in your handlers, as the examples above do.

## Why use `run_subtemplates()`

Before the helper existed, every monorepo hook implemented its own loop:

```python
# Old pattern, do not copy into new templates.
funcs = {k: v for k, v in globals().items() if k.startswith("generate_")}
for template_id, title, enabled in subtemplates:
    template_slug = template_id.replace("/", "_").replace("-", "")
    func_name = f"generate_{template_slug}"
    func = funcs.get(func_name)
    if not func:
        raise ValueError(f"No handler for {template_id}")
    ...
```

Using `run_subtemplates()` gives you:

- **Explicit dispatch.** Handlers are wired up in a visible dictionary rather than discovered by name munging.
- **Consistent logging and deep copies.** The helper prints each step, gives each handler its own copy of the context, and runs handlers in quiet mode, which keeps the console output of nested generations out of the main run.
- **A default for entries without a handler.** See Step 3 for where it generates.
- **Flexible entries.** Besides the `[id, title, enabled]` lists that Cookieplone passes, a hook that rewrites `context["__cookieplone_subtemplates"]` can use dictionaries with a `folder_name` key, or lists with `folder_name` as a fourth item. A `folder_name` of `.` merges the sub-template into the project directory.

## Full example

The complete reference implementation is the hook of the `project` template in the `cookieplone-templates` repository:

> [`templates/projects/monorepo/hooks/post_gen_project.py`](https://github.com/plone/cookieplone-templates/blob/next/templates/projects/monorepo/hooks/post_gen_project.py)

Read it alongside this guide when you build your own multi-part template.

## Related pages

- {doc}`/concepts/subtemplates`: background on how sub-templates are declared and composed.
- {doc}`run-post-gen-actions`: the post-generation actions that run after the sub-templates.
- {doc}`/reference/schema-v2`: the per-template schema, including `config.subtemplates`.
- {doc}`/how-to-guides/create-a-hidden-template`: hide sub-templates from the main menu.
