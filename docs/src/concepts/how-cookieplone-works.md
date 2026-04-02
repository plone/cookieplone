---
myst:
  html_meta:
    "description": "An explanation of the Cookieplone generation pipeline from repository resolution to file output."
    "property=og:description": "An explanation of the Cookieplone generation pipeline from repository resolution to file output."
    "property=og:title": "How Cookieplone works"
    "keywords": "Cookieplone, pipeline, architecture, hooks, wizard, Cookiecutter, generation"
---

# How Cookieplone works

This page explains the end-to-end pipeline that runs when you execute `cookieplone`.

## The pipeline

When you run `cookieplone`, six steps execute in order:

1. **Repository resolution**
2. **Template selection**
3. **pre_prompt hook**
4. **Wizard (interactive prompts)**
5. **File generation**
6. **Post-generation hooks and cleanup**

---

### 1. Repository resolution

Cookieplone resolves the template repository from one of these sources (in priority order):

1. The `COOKIEPLONE_REPOSITORY` environment variable.
2. The built-in default: `gh:plone/cookieplone-templates`.

The resolved source is a git URL, local path, zip archive, or abbreviated form (`gh:`, `gl:`, `bb:`).
Cookieplone clones or copies the repository to a temporary directory,
checking out the tag or branch specified by `--tag` (default: `next`) or `COOKIEPLONE_REPOSITORY_TAG`.

---

### 2. Template selection

Cookieplone reads the root configuration (`cookieplone-config.json` or `cookiecutter.json`) from the cloned repository to discover available templates.
If you provided a template name on the command line, Cookieplone selects it directly.
Otherwise, it displays an interactive menu.
When the configuration defines groups, Cookieplone first asks you to pick a category, then shows the templates in that category.
When no groups are defined, the flat template list is shown directly.

---

### 3. pre_prompt hook

If the selected template contains a `hooks/pre_prompt.py` file, Cookieplone executes it as a Python script before showing any prompts.
A non-zero exit code causes Cookieplone to abort immediately.

This is the right place to check for required system tools, minimum software versions, or network access.

---

### 4. Wizard (interactive prompts)

Cookieplone reads the template's `cookieplone.json` (v2) or `cookiecutter.json` (v1) schema and presents prompts for each non-computed field.

For each field:

- The default value is shown (pre-filled from the answers file, `default_context`, or the schema default).
- If a validator is wired to the field (via `DEFAULT_VALIDATORS` or the `validator` key), the answer is validated before moving to the next field.
- Computed fields are evaluated silently after all interactive fields are answered.

When `--no-input` is set, Cookieplone skips the prompts and uses defaults directly.

---

### 5. File generation

Cookieplone passes the collected answers to Cookiecutter's file renderer.
Cookiecutter walks the template directory, rendering each filename and file content through Jinja2 using the answers as context.
Built-in filters (see {doc}`/reference/filters`) are available in all Jinja2 expressions.

The rendered files are written to the output directory (default: current working directory).

---

### 6. Post-generation hooks and cleanup

If the template contains `hooks/post_gen_project.py`, Cookieplone executes it in the generated project directory.
A non-zero exit code raises an error; the generated directory is deleted unless `--keep-project-on-failure` is set.

After a successful generation, Cookieplone:

- Writes `.cookieplone.json` to the generated project directory with the answers, for use with `--answers-file` on a future re-run.
- Removes any temporary repository clone created during step 1.

---

## Data flow diagram

```
  cookieplone [TEMPLATE] [EXTRA_CONTEXT] [OPTIONS]
        │
        ▼
  Resolve repository  ←── COOKIEPLONE_REPOSITORY / --tag
        │
        ▼
  Select template  ←── template argument / interactive menu
        │
        ▼
  pre_prompt hook  ←── hooks/pre_prompt.py (optional)
        │
        ▼
  Interactive wizard  ←── cookieplone.json / cookiecutter.json
        │              ←── --answers-file / default_context
        │              ←── DEFAULT_VALIDATORS + per-field validators
        ▼
  Jinja2 file renderer  ←── built-in filters
        │
        ▼
  post_gen_project hook  ←── hooks/post_gen_project.py (optional)
        │
        ▼
  Output directory  →  .cookieplone.json (saved answers)
```

---

## Related pages

- {doc}`/concepts/template-repositories`: how the root repository is structured.
- {doc}`/concepts/validators-and-filters`: when validators and filters run.
- {doc}`/concepts/computed-defaults`: how computed field values are resolved.
- {doc}`/concepts/answers-and-replay`: how saved answers feed back into a re-run.
- {doc}`/how-to-guides/write-a-pre-prompt-hook`: write a `pre_prompt` hook.
- {doc}`/how-to-guides/debug-a-failed-generation`: diagnose failures in the pipeline.
