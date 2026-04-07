---
myst:
  html_meta:
    "description": "How to orchestrate sub-template generation from a post-generation hook using run_subtemplates and custom handlers."
    "property=og:description": "How to orchestrate sub-template generation from a post-generation hook using run_subtemplates and custom handlers."
    "property=og:title": "Call sub-templates from a hook"
    "keywords": "Cookieplone, sub-templates, post_gen_project, run_subtemplates, handlers, monorepo"
---

# Call sub-templates from a hook

This guide shows how to drive sub-template generation from a top-level template's `post_gen_project.py`, using {py:func}`cookieplone.utils.subtemplates.run_subtemplates` and a dictionary of custom handlers.
It uses the `monorepo` project template from [`plone/cookieplone-templates`](https://github.com/plone/cookieplone-templates) as a reference: that template composes a full Plone project out of seven sub-templates (backend, frontend, docs, cache, project settings, CI, and VS Code configuration).

## Prerequisites

- You already have a template repository that declares sub-templates (see {doc}`/concepts/subtemplates`).
- Your main template's `cookieplone.json` lists the sub-templates to run under `config.subtemplates`.
- You know which sub-templates need custom handling (extra context, folder rewrites, post-processing) and which can fall through to the default generator.

## Step 1: Import the helper

At the top of `hooks/post_gen_project.py`:

```python
from collections import OrderedDict
from pathlib import Path

from cookieplone import generator
from cookieplone.utils import console, files, git, npm, plone
from cookieplone.utils.subtemplates import run_subtemplates

context: OrderedDict = {{cookiecutter}}
versions: dict | OrderedDict = {{versions}}
```

The `{{cookiecutter}}` and `{{versions}}` markers are Jinja substitutions that Cookiecutter fills in with the rendered context and the loaded `global_versions` mapping.

## Step 2: Write one handler per sub-template

A handler must have the signature `(context: OrderedDict, output_dir: Path) -> Path` and return the directory that the sub-template generated into.
`run_subtemplates()` passes a deep copy of the context to each handler, so mutating `context` in place is safe.

### A simple handler

The backend sub-template needs a headless flavor and should skip CI/docs scaffolding (those belong to the parent project), then clean up residual `.git` artifacts:

```python
BACKEND_ADDON_REMOVE = [".git"]
TEMPLATES_FOLDER = "templates"


def generate_addons_backend(context: OrderedDict, output_dir: Path) -> Path:
    """Run the Plone backend add-on generator."""
    folder_name = "backend"
    context["feature_headless"] = "1"
    context["initialize_ci"] = "0"
    context["initialize_documentation"] = "0"
    path = generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/add-ons/backend",
        output_dir,
        folder_name,
        context,
        BACKEND_ADDON_REMOVE,
    )
    files.remove_files(output_dir / folder_name, BACKEND_ADDON_REMOVE)
    return path
```

Key points:

- The handler **mutates context** freely; the copy is local.
- It returns the `Path` produced by {py:func}`cookieplone.generator.generate_subtemplate`.
- Extra cleanup (`files.remove_files`) happens after generation but still inside the handler.

### A handler with post-processing

The frontend handler does more work: it normalizes scoped npm package names, disables release automation in `.release-it.json`, and rewrites hard-coded repository URLs in the generated files.

```python
def generate_addons_frontend(context: OrderedDict, output_dir: Path) -> Path:
    """Run the Volto add-on generator."""
    folder_name = "frontend"
    context = _fix_frontend_addon_name(context)
    frontend_addon_name = context["frontend_addon_name"]
    context["initialize_documentation"] = "0"
    context["initialize_ci"] = "0"
    path = generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/add-ons/frontend",
        output_dir,
        folder_name,
        context,
        FRONTEND_ADDON_REMOVE,
    )
    # Disable release automation that only makes sense for stand-alone add-ons.
    release_it_path = path / "packages" / frontend_addon_name / ".release-it.json"
    if release_it_path.is_file():
        data = json.loads(release_it_path.read_text())
        data["github"]["release"] = False
        data["plonePrePublish"]["publish"] = False
        data["npm"]["publish"] = False
        release_it_path.write_text(json.dumps(data, indent=2))
    # Rewrite stand-alone repository URLs to point at the parent monorepo.
    _find_replace_in_folder(path, {
        "https://github.com/.../frontend_addon_name":
            "{{ cookiecutter.__repository_url }}",
    })
    return path
```

### A handler with a composed context

Some sub-templates run against a narrower context built from the parent's answers. For example, the GitHub Actions CI sub-template only needs a handful of derived values:

```python
def generate_ci_gh_project(context: OrderedDict, output_dir: Path) -> Path:
    """Generate GitHub Actions workflows for the monorepo."""
    ci_context = OrderedDict({
        "npm_package_name": context["__npm_package_name"],
        "container_image_prefix": context["__container_image_prefix"],
        "python_version": versions["backend_python"],
        "node_version": context["__node_version"],
        "has_cache": context["devops_cache"],
        "has_docs": context["initialize_documentation"],
        "has_deploy": context["devops_gha_deploy"],
        "__cookieplone_repository_path": context["__cookieplone_repository_path"],
    })
    return generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/ci/gh_project",
        output_dir,
        ".github",
        ci_context,
    )
```

The generated files land in `.github/` at the project root, which is why the handler passes `folder_name=".github"` explicitly.

### A handler that rewrites the output directory

Some sub-templates need to be rendered **as** the parent directory. For example, a cache sub-template that adds files next to the project without introducing a new folder:

```python
def generate_sub_cache(context: OrderedDict, output_dir: Path) -> Path:
    """Add cache structure to the existing project folder."""
    folder_name = output_dir.name
    parent_dir = output_dir.parent
    return generator.generate_subtemplate(
        f"{TEMPLATES_FOLDER}/sub/cache", parent_dir, folder_name, context,
    )
```

## Step 3: Register the handlers

Collect every handler in a module-level dict keyed by the sub-template `id` (the same `id` declared in `config.subtemplates` in your `cookieplone.json`):

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

If a sub-template is declared in `config.subtemplates` but **not** present in this dict, `run_subtemplates()` will fall back to a default call with the entry's `folder_name`.
That fallback is useful for straightforward sub-templates that only need the defaults.

## Step 4: Invoke `run_subtemplates()` from `main()`

Inside the `main()` function of your post-generation hook, replace any manual loop over `__cookieplone_subtemplates` with a single call:

```python
def main():
    output_dir = Path.cwd()

    # {{ cookiecutter.__cookieplone_subtemplates }}
    run_subtemplates(context, output_dir, handlers=SUBTEMPLATE_HANDLERS)

    # Continue with other post-generation tasks (namespace packages,
    # code formatting, git initialization, ...).
    plone.create_namespace_packages(
        output_dir / "backend/src/packagename",
        context.get("python_package_name"),
        style="native",
    )


if __name__ == "__main__":
    main()
```

The trailing `# {{ cookiecutter.__cookieplone_subtemplates }}` comment is **important**: it ensures Cookiecutter treats the sub-templates list as a rendered context value, which is what `run_subtemplates()` then reads at runtime.

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

- **Explicit dispatch.** Handlers are wired up in a visible dict rather than discovered by name munging.
- **Consistent logging and deep-copying.** The helper prints each step and guarantees that handlers can not accidentally mutate a shared context.
- **Default fallback.** Simple sub-templates no longer require a matching handler at all.
- **Schema compatibility.** Both the legacy `[id, title, enabled]` format and the dict format with `folder_name` are accepted transparently.

## Full example

The complete reference implementation is the monorepo template in the `cookieplone-templates` repository:

> [`templates/projects/monorepo/hooks/post_gen_project.py`](https://github.com/plone/cookieplone-templates/blob/next/templates/projects/monorepo/hooks/post_gen_project.py)

Read it alongside this guide when you build your own multi-part template.

## Related pages

- {doc}`/concepts/subtemplates`: background on how sub-templates are declared and composed.
- {doc}`/reference/schema-v2`: the per-template schema, including `config.subtemplates`.
- {doc}`/how-to-guides/create-a-hidden-template`: hide sub-templates from the main menu.
