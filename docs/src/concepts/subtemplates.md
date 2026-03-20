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

## The `templates` key

Sub-templates are declared in the root `cookiecutter.json` under the `templates` key:

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

## Calling a sub-template from a hook

A post-generation hook in the `project` template calls the sub-templates after the main template is rendered:

```python
# hooks/post_gen_project.py
import subprocess
import sys


def run_sub_template(template_name: str) -> None:
    result = subprocess.run(
        [
            sys.executable, "-m", "cookieplone",
            template_name,
            "--no-input",
            "--answers", ".cookieplone.json",
            "--output-dir", "..",
        ],
        check=False,
    )
    if result.returncode != 0:
        sys.exit(result.returncode)


if __name__ == "__main__":
    run_sub_template("backend")
    run_sub_template("frontend")
```

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
- {doc}`/how-to-guides/create-a-hidden-template`: mark a template as hidden.
- {doc}`/reference/schema-v2`: the per-template schema format.
