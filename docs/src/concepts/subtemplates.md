---
myst:
  html_meta:
    "description": "An explanation of how Cookieplone template repositories expose multiple sub-templates and how they compose."
    "property=og:description": "An explanation of how Cookieplone template repositories expose multiple sub-templates and how they compose."
    "property=og:title": "Sub-templates"
    "keywords": "Cookieplone, sub-templates, composite templates, post_gen_project, hidden, templates key"
---

# Sub-templates

A Cookieplone template repository can expose multiple independent templates through a single root `cookiecutter.json`.
These are called sub-templates.

## Why sub-templates exist

A large project (for example, a full Plone site) may consist of several composable parts:

- A backend package.
- A frontend add-on.
- A Docker Compose configuration.
- A CI/CD pipeline.

Rather than bundling everything into one monolithic template, you can define each part as a separate sub-template.
A post-generation hook in the main template then calls the sub-templates programmatically to assemble the final project.

This keeps each sub-template focused, testable, and reusable independently.

## Declaring sub-templates

There are two levels where sub-templates appear in a Cookieplone repository.

### Repository-level `templates` key

The root `cookiecutter.json` lists all templates the repository provides under the `templates` key:

```json
{
  "templates": {
    "project": {
      "path": "./templates/project",
      "title": "A Plone project",
      "description": "Full Plone project with backend and frontend."
    },
    "backend": {
      "path": "./templates/backend",
      "title": "Backend package",
      "description": "Plone backend package only.",
      "hidden": true
    },
    "frontend": {
      "path": "./templates/frontend",
      "title": "Volto frontend add-on",
      "description": "Volto frontend add-on only.",
      "hidden": true
    }
  }
}
```

In this example:

- `project` is the main template, visible to users.
- `backend` and `frontend` are sub-templates called programmatically; they are hidden from the menu.

### Template-level: `config.subtemplates`

Inside each template's `cookieplone.json` (v2 format), the `config.subtemplates` array declares which sub-templates should run after generation.
Each entry has an `id`, a `title`, and an `enabled` field:

```json
{
  "config": {
    "subtemplates": [
      {"id": "sub/backend", "title": "Backend", "enabled": "1"},
      {"id": "sub/frontend", "title": "Frontend", "enabled": "{{ cookiecutter.has_frontend }}"}
    ]
  }
}
```

The `enabled` field can be a static value (`"1"` or `"0"`) or a Jinja2 expression.
Expressions are rendered against the current template context after the user completes the wizard, allowing sub-templates to be conditionally enabled based on user answers.

During generation, these entries are converted into `[id, title, enabled]` lists and injected into the template context as `__cookieplone_subtemplates`, where post-generation hooks can read them.

See {doc}`/reference/schema-v2` for the full specification of the `config.subtemplates` format.

## Calling sub-templates from a hook

A post-generation hook in the main template triggers the sub-templates after the top-level project is rendered.
Cookieplone ships a helper, {py:func}`cookieplone.utils.subtemplates.run_subtemplates`, that reads the `__cookieplone_subtemplates` entries from the context and dispatches each one:

```python
# hooks/post_gen_project.py
from collections import OrderedDict
from pathlib import Path

from cookieplone.utils.subtemplates import run_subtemplates

context: OrderedDict = {{cookiecutter}}


def main():
    output_dir = Path.cwd()
    # {{ cookiecutter.__cookieplone_subtemplates }}
    run_subtemplates(context, output_dir)


if __name__ == "__main__":
    main()
```

For each enabled entry, `run_subtemplates()`:

1. Skips it (with a log line) when `enabled` evaluates to `0`.
2. Calls a **custom handler** if you registered one for that sub-template `id`.
3. Otherwise falls back to a default call to {py:func}`cookieplone.generator.generate_subtemplate` using the entry's `folder_name`.

### Custom handlers

Most real projects need per-sub-template tweaks: injecting extra context keys, rewriting the output folder, or post-processing generated files.
Pass a `handlers` dict mapping `template_id` → callable with signature `(context, output_dir) -> Path`:

```python
from cookieplone.utils.subtemplates import run_subtemplates


def generate_backend(context, output_dir):
    context["feature_headless"] = "1"
    return generator.generate_subtemplate(
        "templates/add-ons/backend", output_dir, "backend", context,
    )


SUBTEMPLATE_HANDLERS = {
    "add-ons/backend": generate_backend,
}

run_subtemplates(context, output_dir, handlers=SUBTEMPLATE_HANDLERS)
```

Handlers receive a deep copy of the context, so in-place mutations are safe and do not leak across sub-templates.

For a full real-world example that registers seven handlers covering backend, frontend, docs, CI, IDE, and shared sub-templates, see {doc}`/how-to-guides/call-subtemplates-from-a-hook`.

## Hidden sub-templates

Sub-templates that users should not invoke directly are marked `"hidden": true`.
This keeps the main menu clean while still allowing programmatic access.

A user who wants to invoke a hidden template can pass `--all` to see it:

```console
cookieplone --all
```

Or pass the template name directly:

```console
cookieplone backend
```

## Independent sub-templates

Sub-templates do not have to be hidden.
A repository can expose several equally prominent templates—for example, a `project` template and a standalone `addon` template—each runnable on its own.

## Related pages

- {doc}`/concepts/template-repositories`: how the root `cookiecutter.json` is structured.
- {doc}`/how-to-guides/call-subtemplates-from-a-hook`: walk through a real post-generation hook using `run_subtemplates()`.
- {doc}`/how-to-guides/create-a-hidden-template`: mark a template as hidden.
- {doc}`/reference/schema-v2`: the per-template schema format.
