---
myst:
  html_meta:
    "description": "An explanation of how a Cookieplone template generates other templates as sub-templates, and how they are declared and run."
    "property=og:description": "An explanation of how a Cookieplone template generates other templates as sub-templates, and how they are declared and run."
    "property=og:title": "Sub-templates"
    "keywords": "Cookieplone, sub-templates, config.subtemplates, run_subtemplates, post_gen_project, hidden templates"
---

# Sub-templates

A sub-template is a template that another template generates during its own run.
The `project` template of [`cookieplone-templates`](https://github.com/plone/cookieplone-templates), for example, generates a backend add-on, a frontend add-on, documentation, cache settings, editor settings, and CI configuration as sub-templates.

## Why sub-templates exist

A large project, such as a full Plone site, consists of several composable parts:

- A backend package.
- A frontend add-on.
- A Docker Compose configuration.
- A CI/CD pipeline.

Rather than bundling everything into one monolithic template, you can define each part as a separate template.
A post-generation hook in the main template then generates the parts to assemble the final project.

This keeps each part focused, testable, and reusable on its own.

## Declare sub-templates

A template lists its sub-templates in `config.subtemplates` of its `cookieplone.json`.
This excerpt comes from the `project` template of `cookieplone-templates`:

```json
{
  "config": {
    "subtemplates": [
      {"id": "add-ons/backend", "title": "Setup Backend", "enabled": "1"},
      {"id": "add-ons/frontend", "title": "Setup Frontend", "enabled": "{{ '1' if cookiecutter.feature_headless else '0' }}"},
      {"id": "sub/cache", "title": "Setup Cache", "enabled": "{{ '1' if cookiecutter.devops_cache else '0' }}"}
    ]
  }
}
```

| Key | Description |
|---|---|
| `id` | Path of the sub-template's directory under the repository's `templates/` directory: `add-ons/backend` is `templates/add-ons/backend`. It is not a template ID from `cookieplone-config.json`. |
| `title` | Label that Cookieplone prints when it generates or skips the sub-template. |
| `enabled` | `"1"` to generate the sub-template, `"0"` to skip it, or a Jinja2 expression that renders to one of them. |

```{important}
`enabled` must render to `1` or `0`.
A boolean answer renders as `True` or `False`, which `run_subtemplates` can't convert to a number, so the post-generation hook fails.
Write `{{ '1' if cookiecutter.feature_headless else '0' }}`, not `{{ cookiecutter.feature_headless }}`.
```

After the wizard, Cookieplone renders each `enabled` value, and passes the entries to the template's hooks in the context key `__cookieplone_subtemplates`, as `[id, title, enabled]` lists.

See {doc}`/reference/schema-v2` for the full specification of `config.subtemplates`.

## Generate sub-templates from a hook

Cookieplone doesn't generate sub-templates by itself.
The template's `hooks/post_gen_project.py` calls {py:func}`cookieplone.utils.subtemplates.run_subtemplates`:

```python
# hooks/post_gen_project.py
from collections import OrderedDict
from pathlib import Path

from cookieplone.utils.subtemplates import run_subtemplates

context: OrderedDict = {{cookiecutter}}
versions: dict = {{versions}}


def main():
    output_dir = Path().cwd()
    run_subtemplates(context, output_dir, global_versions=versions)


if __name__ == "__main__":
    main()
```

Cookieplone renders the hook before running it, so `context` holds the answers and `versions` holds the version pins.
Passing `global_versions=versions` makes `{{ versions.<key> }}` work in the files of the sub-templates.

For each entry, `run_subtemplates`:

1. Skips it when `enabled` is `0`, and prints its title as ignored.
2. Calls the handler registered for its `id`, if there is one.
3. Otherwise, generates `templates/<id>` with a copy of the current answers, without asking any question.
   It generates in the project directory, with the project's name as folder name, which nests most sub-templates in a folder named like the project.
   Register a handler whenever the location matters.

It returns a dictionary that maps the `id` of each generated sub-template to the generated path.

### Custom handlers

A handler adjusts the answers or the output location for one sub-template.
It receives a deep copy of the context and the output directory, so its changes don't leak to other sub-templates, and it returns the generated path.
This handler is adapted from the `project` template, and generates the backend add-on into a `backend` folder:

```python
from cookieplone import generator


def generate_addons_backend(context: OrderedDict, output_dir: Path) -> Path:
    """Generate the backend add-on into a backend folder."""
    context["initialize_ci"] = False
    context["initialize_documentation"] = False
    return generator.generate_subtemplate(
        "templates/add-ons/backend",
        output_dir,
        "backend",
        context,
        global_versions=versions,
    )


SUBTEMPLATE_HANDLERS = {
    "add-ons/backend": generate_addons_backend,
}


def main():
    output_dir = Path().cwd()
    run_subtemplates(
        context, output_dir, handlers=SUBTEMPLATE_HANDLERS, global_versions=versions
    )
```

The keys of the handlers dictionary are sub-template IDs.
{py:func}`cookieplone.generator.generate_subtemplate` is deprecated for looping over sub-templates yourself, but handlers still call it: `run_subtemplates` runs handlers in quiet mode, which also silences its deprecation warning.

For the complete hook of the `project` template, with seven handlers, see {doc}`/how-to-guides/call-subtemplates-from-a-hook`.

## Sub-templates and the menu

A sub-template's `id` is a path, so a sub-template doesn't need an entry in `cookieplone-config.json`.
A directory can still appear in both places, under different IDs:

- `templates/add-ons/backend` is the visible `backend_addon` template in the menu, and the `add-ons/backend` sub-template of `project`.
- `templates/ci/gh_project` is the `ci/gh_project` sub-template of `project`, and the hidden `ci_gh_project` template, in the hidden `ci` group.

List a sub-template in `cookieplone-config.json` when people should also run it on its own.
Mark it hidden when they should not see it in the menu.

## Related pages

- {doc}`/concepts/template-repositories`: how `cookieplone-config.json` is structured.
- {doc}`/how-to-guides/call-subtemplates-from-a-hook`: walk through a real post-generation hook using `run_subtemplates()`.
- {doc}`/how-to-guides/create-a-hidden-template`: hide a template or a group.
- {doc}`/reference/schema-v2`: the per-template schema format.
