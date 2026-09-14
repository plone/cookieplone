---
myst:
  html_meta:
    "description": "Terms and definitions used throughout the Cookieplone documentation."
    "property=og:description": "Terms and definitions used throughout the Cookieplone documentation."
    "property=og:title": "Glossary"
    "keywords": "Cookieplone, glossary, terms, template, template repository, sub-template, hook, answers file"
---

(glossary-label)=

# Glossary

Terms and definitions used throughout the Cookieplone documentation.

```{glossary}
:sorted: true

add-on
    A package that extends Plone.
    A backend add-on is a Python package, and a frontend add-on is a JavaScript package for {term}`Volto` or {term}`Aurora`.
    The `backend_addon`, `frontend_addon`, `aurora_addon`, and `monorepo_addon` templates generate add-ons.

    -   [Plone core add-ons](https://github.com/collective/awesome-plone#readme)
    -   [Volto add-ons](https://github.com/collective/awesome-volto#readme)
    -   [Add-ons tagged with the trove classifier `Framework :: Plone` on PyPI](https://pypi.org/search/?c=Framework+%3A%3A+Plone)

answers file
    A JSON file with answers to the questions of a template.
    Cookieplone writes `.cookieplone.json` into each generated project, and reads an answers file that you pass with `--answers-file`.
    See {doc}`/how-to-guides/use-an-answers-file`.

Aurora
    Plone Aurora, a Plone frontend in alpha.
    The `aurora_cmfplone`, `aurora_nick`, `aurora_nick_embedded`, and `aurora_addon` templates generate projects and add-ons for it.

Classic UI
    The Plone user interface that the backend renders, without a separate JavaScript frontend.
    The `project` template generates a Classic UI project when you answer no to "Use Volto as frontend?".

computed field
    A field with `"format": "computed"` in the `cookieplone.json` of a template.
    Cookieplone doesn't ask it.
    It renders the default of the field, a Jinja2 expression, from the answers.
    See {doc}`/concepts/computed-defaults`.

constant field
    A field with `"format": "constant"` in the `cookieplone.json` of a template.
    Cookieplone doesn't ask it, and uses its default as written, without rendering it.

Cookiecutter
    [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/) is a command line utility that creates projects from templates.
    Cookieplone uses it to render the files of a template.
    A Cookieplone template describes its questions in `cookieplone.json` instead of `cookiecutter.json`.

Cookieplone
    [Cookieplone](https://github.com/plone/cookieplone) generates {term}`Plone` codebases from templates.
    On top of {term}`Cookiecutter`, it adds template repositories with groups, a question wizard, validators, Jinja2 filters, and sub-templates.
    Run it with `uvx cookieplone`.

cookieplone-templates
    [cookieplone-templates](https://github.com/plone/cookieplone-templates) is the {term}`template repository` that Cookieplone uses by default.
    The Plone community maintains it.
    It has templates for Plone projects, add-ons, and documentation.
    See {doc}`/reference/templates/index`.

extends
    A key of `cookieplone-config.json` that builds a {term}`template repository` on top of an upstream repository.
    The downstream repository inherits the upstream templates, and can add or replace templates, or {term}`overlay` them.
    See {doc}`/how-to-guides/extend-an-upstream-template-repository`.

group
    A named set of templates in `cookieplone-config.json`.
    When you run Cookieplone without a template ID, it lists the groups first, then the templates of the group you choose.

hidden template
    A template marked `"hidden": true` in `cookieplone-config.json`.
    Cookieplone leaves it out of the menu unless you pass `--all`, and runs it when you pass its ID.

hook
    A script in the `hooks` folder of a template that Cookieplone runs at a fixed point of a generation: `pre_prompt`, `pre_gen_project`, or `post_gen_project`.
    See {doc}`/concepts/hooks`.

Markedly Structured Text
MyST
    [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/) is a flavor of Markdown for {term}`Sphinx`.
    The Cookieplone documentation uses it.

Nick
    A Plone backend written in Node.js.
    The `volto_nick`, `aurora_nick`, and `aurora_nick_embedded` templates use it.

overlay
    A downstream template with a `path`, in a repository that `extends` an upstream repository.
    Cookieplone copies the files of the upstream template first, then the downstream files on top.
    See {doc}`/how-to-guides/extend-an-upstream-template-repository`.

Plone
    [Plone](https://plone.org/) is an open source content management system for websites, intranets, and custom applications.

post_gen_project
    The {term}`hook` that runs in the generated project after Cookieplone renders the files.
    The official templates use it to run {term}`sub-templates <sub-template>` and post-generation actions.

pre_prompt
    The {term}`hook` that runs before the first question, in a temporary copy of the template.
    The official templates use it to check for the tools they need.

renderer
    The {term}`tui_forms` component that draws the questions.
    Cookieplone uses the renderer named by `COOKIEPLONE_RENDERER`, then the one in `config.renderer` of the repository, and falls back to `cookiecutter`.
    `cookieplone-templates` sets `rich`.
    With `--no-input`, Cookieplone uses the `noinput` renderer, which asks nothing.

replay file
    A JSON file with the full context of a generation, including computed values.
    `--replay` and `--replay-file` generate a project again from it.
    See {doc}`/concepts/answers-and-replay`.

Sphinx
    [Sphinx](https://www.sphinx-doc.org/en/master/) builds documentation from reStructuredText or {term}`MyST` sources.
    The Cookieplone documentation and the `documentation_starter` template use it.

sub-template
    A template that another template runs from its `post_gen_project` hook, to generate part of a project.
    Sub-templates are usually hidden.
    See {doc}`/concepts/subtemplates`.

template
    A folder with a `cookieplone.json` file, which describes the questions, and the files and folders to render.
    A {term}`template repository` lists its templates in `cookieplone-config.json`, each under an ID.

template repository
    A directory, git repository, or zip archive with a `cookieplone-config.json` file at its root, and the templates that the file lists.
    See {doc}`/concepts/template-repositories`.

tui_forms
    The Python library that turns the questions of a template into a form, and asks them through a {term}`renderer`.

uv
uvx
    [uv](https://docs.astral.sh/uv/) is a Python package and project manager.
    `uvx` runs a Python tool without installing it.
    Running `uvx cookieplone` is the recommended way to use {term}`Cookieplone`.
    See {doc}`/install`.

versions namespace
    The version pins that a template reads as `{{ versions.<key> }}`.
    They come from `config.versions` in `cookieplone-config.json`, and from the template's own `config.versions`, which takes precedence.

Volto
    The React frontend of Plone 6.
    The `project` template generates a Volto frontend when you answer yes to "Use Volto as frontend?", and `frontend_addon` generates Volto add-ons.
```
