---
myst:
  html_meta:
    "description": "The history of Cookieplone: why it exists, what it adds over raw Cookiecutter, and how it has evolved."
    "property=og:description": "The history of Cookieplone: why it exists, what it adds over raw Cookiecutter, and how it has evolved."
    "property=og:title": "History"
    "keywords": "Cookieplone, history, background, Cookiecutter, Plone, design decisions"
---

(background)=

# History

## The problem

The Plone community maintained many separate template repositories over the years.
Each repository followed slightly different conventions, used different variable names, and required manual updates when community standards changed.
New contributors faced inconsistent setups, and experienced developers spent time reconciling differences between projects.
There was no single entry point that worked for all Plone project types.

## Starting as a Cookiecutter wrapper

Cookieplone started as a thin wrapper around [Cookiecutter](https://cookiecutter.readthedocs.io/), a widely used Python project scaffolding tool.
Cookiecutter already handled template rendering via Jinja2, git-based template fetching, and a simple JSON-based schema (`cookiecutter.json`).

Rather than replace it, Cookieplone extended it with:

- Built-in validators for common Plone fields such as `plone_version`, `python_package_name`, and `hostname`.
- Built-in Jinja2 filters for transformations such as `package_name`, `pascal_case`, `latest_plone`, and `node_version_for_volto`.
- A sub-template mechanism, allowing a single repository to expose multiple related templates (for example, backend add-on, frontend add-on, and full project) that share validators and filters.
- Sane defaults for Plone-specific configuration, drawn from the active Plone release matrix.

## Evolving into a fuller solution

As the community consolidated templates into a single `cookieplone-templates` repository, Cookieplone took on more responsibilities:

- A terminal user interface (TUI) for interactive prompts, replacing Cookiecutter's plain `input()` calls.
- A richer schema format (`cookieplone.json`) that supports typed fields, computed defaults, and per-field validators, while remaining backward-compatible with plain `cookiecutter.json`.
- Template discovery: a root `cookiecutter.json` in a repository can declare multiple templates, and Cookieplone presents them as a menu.
- Support for any template source—local paths, git URLs, zip archives, and abbreviations such as `gh:`, `gl:`, and `bb:`: not only `cookieplone-templates`.

## Design decisions

**Why keep Cookiecutter as a dependency?**
Cookiecutter's hook system, file rendering, and replay mechanism are mature and well-tested.
Replacing them would duplicate significant work with little benefit for end-users.
Cookieplone stays thin where Cookiecutter is strong and adds only where Cookiecutter is absent.

**Why a separate templates repository?**
Separating the tool (`cookieplone`) from the templates (`cookieplone-templates`) means the templates can evolve at their own pace, and third parties can provide their own template repositories without forking Cookieplone itself.

**Why `uvx`?**
`uvx` runs Cookieplone in an isolated environment without requiring the user to manage a virtual environment.
This lowers the barrier to entry for Plone beginners significantly.
