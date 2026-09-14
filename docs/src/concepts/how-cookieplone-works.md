---
myst:
  html_meta:
    "description": "An explanation of the Cookieplone generation pipeline from repository resolution to file output."
    "property=og:description": "An explanation of the Cookieplone generation pipeline from repository resolution to file output."
    "property=og:title": "How Cookieplone works"
    "keywords": "Cookieplone, pipeline, architecture, hooks, wizard, tui_forms, extends, min_version, summary, Cookiecutter, generation"
---

# How Cookieplone works

This page explains the end-to-end pipeline that runs when you execute `cookieplone`.

## The pipeline

When you run `cookieplone`, these steps execute in order:

1. **Repository resolution**
2. **Repository configuration**
3. **Template selection**
4. **`pre_prompt` hook**
5. **Wizard**
6. **File generation**, with the `pre_gen_project` and `post_gen_project` hooks
7. **Answers, cleanup, and summary**

---

### 1. Repository resolution

Cookieplone resolves the template repository from one of these sources (in priority order):

1. The `COOKIEPLONE_REPOSITORY` environment variable.
2. The built-in default: `gh:plone/cookieplone-templates`, the official [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) repository.

The source is a git URL, a local directory, a zip archive, or an abbreviated form (`gh:`, `gl:`, `bb:`).
Cookieplone uses a local directory in place.
It downloads a git repository or a zip archive into the directory set by `cookiecutters_dir`, `~/.cookiecutters/` by default, and checks out the tag or branch set by `--tag` or `COOKIEPLONE_REPOSITORY_TAG` (default: `main`).
When none of `COOKIEPLONE_REPOSITORY`, `--tag`, and `COOKIEPLONE_REPOSITORY_TAG` is set, and the `main` branch has no `cookieplone-config.json`, Cookieplone checks out `next` instead.

---

### 2. Repository configuration

Cookieplone reads the repository's `cookieplone-config.json`.
When the file has `extends`, Cookieplone resolves the upstream repositories and merges their configuration underneath this one (see {ref}`repo-extends`).

Cookieplone validates the result, then checks `config.min_version`.
When the running Cookieplone is older than that version, it stops and prints the command to upgrade.

The configuration also sets the version pins available to all templates (`config.versions`), the wizard's renderer (`config.renderer`), and the summary screen (`config.summary`).

---

### 3. Template selection

If you passed a template ID on the command line, or an answers file with a `__template__` key, Cookieplone selects that template directly, even when it's hidden.
Otherwise, it displays an interactive menu.
When the configuration defines groups, Cookieplone first asks you to pick a category, then shows the templates in that category.
Hidden groups and templates are left out of the menu unless you pass `--all`.

---

### 4. `pre_prompt` hook

If the selected template has a `pre_prompt` hook, Cookieplone runs it in a temporary copy of the template directory, before any question.
The hook has no answers to work with.
When it fails, Cookieplone stops with `Sanity checks failed.`

This is the right place to check for required system tools, software versions, or network access.
See {doc}`/concepts/hooks`.

---

### 5. Wizard

Cookieplone reads the template's `cookieplone.json` and asks a question for each field that is neither computed nor constant.

A `tui_forms` renderer draws the questions.
Cookieplone uses the renderer named by the `COOKIEPLONE_RENDERER` environment variable, then the one in `config.renderer`, and falls back to `cookiecutter`.
`cookieplone-templates` sets `rich`.

For each field:

- The default value comes from, in order of precedence, the extra context, the answers file, the user configuration's `default_context`, and the schema default.
- If a validator is wired to the field (via `DEFAULT_VALIDATORS` or the `validator` key), the answer is validated before moving to the next field.
- Computed fields are evaluated silently after all interactive fields are answered.

After the last question, Cookieplone shows your answers and asks you to confirm them.
If you decline, the wizard starts again, with your answers as the defaults.

When `--no-input` is set, Cookieplone uses a renderer that asks nothing and shows no confirmation.
It uses the defaults, which still pass through their validators.

---

### 6. File generation

Cookieplone creates the project directory in the output directory (default: current working directory), and runs the template's `pre_gen_project` hook there.

Then Cookiecutter walks the template directory, rendering each file name, directory name, and file content through Jinja2, with the answers as context.
The filters that the template lists in `config.extensions` (see {doc}`/reference/filters`) are available in these expressions.
Files that match `config.no_render` are copied without rendering.

Finally, Cookieplone runs the template's `post_gen_project` hook in the project directory.
Templates generate their sub-templates from this hook (see {doc}`/concepts/subtemplates`).

When `pre_gen_project` or `post_gen_project` fails, Cookieplone stops, and deletes the project directory it created, unless `--keep-project-on-failure` is set.

---

### 7. Answers, cleanup, and summary

After generation, Cookieplone:

- Writes `.cookieplone.json` to the generated project directory with the answers, for use with `--answers-file` on a future re-run.
- Saves a replay file in its replay directory, `~/.cookiecutter_replay/` by default.
- Removes the temporary copies it made, such as the one used by the `pre_prompt` hook.
- Shows a summary screen, when the repository enables `config.summary`.
  The screen names the template and the project location, followed by the configured message, thanks, and signature.

---

## Data flow diagram

```text
  cookieplone [TEMPLATE] [EXTRA_CONTEXT] [OPTIONS]
        │
        ▼
  Resolve repository  ←── COOKIEPLONE_REPOSITORY / --tag
        │
        ▼
  Read configuration  ←── cookieplone-config.json, extends, min_version
        │
        ▼
  Select template  ←── template argument / answers file / menu
        │
        ▼
  pre_prompt hook  ←── hooks/pre_prompt.py (optional)
        │
        ▼
  Wizard (tui_forms)  ←── cookieplone.json
        │              ←── --answers-file / extra context / default_context
        │              ←── DEFAULT_VALIDATORS + per-field validators
        ▼
  pre_gen_project hook  ←── hooks/pre_gen_project.py (optional)
        │
        ▼
  Jinja2 file renderer  ←── filters from config.extensions
        │
        ▼
  post_gen_project hook  ←── hooks/post_gen_project.py (optional)
        │
        ▼
  Output directory  →  .cookieplone.json, replay file, summary screen
```

---

## Related pages

- {doc}`/concepts/template-repositories`: how a template repository is structured.
- {doc}`/concepts/hooks`: what each hook does and how failures are handled.
- {doc}`/concepts/validators-and-filters`: when validators and filters run.
- {doc}`/concepts/computed-defaults`: how computed field values are resolved.
- {doc}`/concepts/answers-and-replay`: how saved answers feed back into a re-run.
- {doc}`/how-to-guides/write-a-pre-prompt-hook`: write a `pre_prompt` hook.
- {doc}`/how-to-guides/debug-a-failed-generation`: diagnose failures in the pipeline.
