---
myst:
  html_meta:
    "description": "An explanation of the hooks a Cookieplone template can run, when each one runs, and what happens when a hook fails."
    "property=og:description": "An explanation of the hooks a Cookieplone template can run, when each one runs, and what happens when a hook fails."
    "property=og:title": "Hooks"
    "keywords": "Cookieplone, hooks, pre_prompt, pre_gen_project, post_gen_project, template, keep-project-on-failure"
---

# Hooks

A hook is a script that Cookieplone runs at a fixed point while it generates a template.
Templates use hooks to check the environment before the first question, and to finish the generated project, for example by generating sub-templates, formatting code, or initializing a git repository.

Hooks come from Cookiecutter, which Cookieplone uses to render templates.

## Hook scripts

A template keeps its hooks in a `hooks/` directory next to its `cookieplone.json`:

```text
templates/
└── features/
    ├── cookieplone.json
    ├── hooks/
    │   ├── pre_prompt.py
    │   ├── pre_gen_project.py
    │   └── post_gen_project.py
    └── {{ cookiecutter.project_slug }}/
```

Every hook is optional.
Cookieplone runs a `.py` hook with the Python interpreter that runs Cookieplone itself, so the hook can import `cookieplone` and its dependencies.
A hook with another extension runs as an executable script.

In [`cookieplone-templates`](https://github.com/plone/cookieplone-templates), most templates have a `pre_prompt.py` and a `post_gen_project.py` hook, and a `pre_gen_project.py` hook is rare.

## When hooks run

| Hook | When it runs | Working directory | Rendered with Jinja2 |
|---|---|---|---|
| `pre_prompt` | After Cookieplone reads the repository configuration, before the first question | A temporary copy of the template directory | No |
| `pre_gen_project` | After the wizard, once the project directory exists, before Cookieplone renders the files | The project directory | Yes |
| `post_gen_project` | After Cookieplone renders the files | The project directory | Yes |

### `pre_prompt`

The `pre_prompt` hook runs before Cookieplone asks anything, so no answers exist yet.
Cookieplone doesn't render it with Jinja2: an expression such as `{{ cookiecutter.project_slug }}` in the script stays as written.
Use it to check what the template needs, such as tools on the `PATH`.

See {doc}`/how-to-guides/write-a-pre-prompt-hook`.

### `pre_gen_project` and `post_gen_project`

Cookieplone renders these hooks with Jinja2 before running them, with the same context as the template files.
A hook reads the answers and the version pins by rendering them into its own code:

```python
from collections import OrderedDict

context: OrderedDict = {{cookiecutter}}
versions: dict = {{versions}}
```

`post_gen_project` is where templates generate their sub-templates and run their final actions.
See {doc}`/how-to-guides/call-subtemplates-from-a-hook` and {doc}`/how-to-guides/run-post-gen-actions`.

## When a hook fails

A hook fails when it exits with a non-zero status.
A Python hook that raises an exception it doesn't catch exits that way too.

- **`pre_prompt`**: Cookieplone prints the hook's output, then `Sanity checks failed.` and `Please review the errors above and try again.`, and exits without creating a project.
- **`pre_gen_project` or `post_gen_project`**: Cookieplone prints a traceback and `Hook script failed (exit status: N)`, and exits.
  When the run created the project directory, Cookieplone deletes it.
  Pass `--keep-project-on-failure` to keep it and inspect what the hook left behind.

See {doc}`/how-to-guides/debug-a-failed-generation`.

## Hooks on existing projects

Cookieplone always runs a template's hooks: no option turns them off.
That includes re-runs over an existing project with `-f` (`--overwrite-if-exists`) or `-s` (`--skip-if-file-exists`), when the project directory already holds files.
Write hooks that can run on a project that already exists: check before you create files, directories, or git repositories.

The formatting handler `run_make_format` ignores the exit status of `make`, so a missing formatter doesn't stop a generation.

## Related pages

- {doc}`/concepts/how-cookieplone-works`: where hooks fit in the generation pipeline.
- {doc}`/how-to-guides/write-a-pre-prompt-hook`: check the environment before the first question.
- {doc}`/how-to-guides/call-subtemplates-from-a-hook`: generate sub-templates from `post_gen_project`.
- {doc}`/how-to-guides/run-post-gen-actions`: run the final actions of a template.
- {doc}`/reference/api/index`: the Python API that hooks use.
