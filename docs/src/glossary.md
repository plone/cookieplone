---
myst:
  html_meta:
    "description": "Terms and definitions used throughout the Cookieplone documentation."
    "property=og:description": "Terms and definitions used throughout the Cookieplone documentation."
    "property=og:title": "Glossary"
    "keywords": "Plone, documentation, glossary, term, definition"
---

Terms and definitions used throughout the Cookieplone documentation.

(glossary-label)=

# Glossary

```{glossary}
:sorted: true

Cookiecutter
    [Cookiecutter](https://cookiecutter.readthedocs.io/) is a command-line utility that creates projects from templates.
    Templates are directories containing a `cookiecutter.json` file that defines variables, and Jinja2-templated files and folder names that are rendered when the project is generated.
    Cookieplone is built on top of Cookiecutter.

Cookieplone
    [Cookieplone](https://github.com/plone/cookieplone) is a wrapper around {term}`Cookiecutter` designed to streamline the creation of {term}`Plone` codebases.
    It provides built-in validators, Jinja2 filters, a sub-template mechanism, and a curated set of templates maintained by the Plone community.
    Run it with `uvx cookieplone`.

cookieplone-templates
    [cookieplone-templates](https://github.com/plone/cookieplone-templates) is the official repository of {term}`Cookieplone` templates maintained by the Plone community.
    It contains templates for backend add-ons, frontend add-ons, and full Plone projects.
    {term}`Cookieplone` uses this repository as its default template source.

uv
uvx
    [uv](https://docs.astral.sh/uv/) is an extremely fast Python package and project manager written in Rust, developed by [Astral](https://astral.sh/).
    `uvx` is the tool runner bundled with `uv` — it installs and runs Python tools in isolated environments without requiring a manual virtual environment setup.
    Running `uvx cookieplone` is the recommended way to use {term}`Cookieplone`.

Plone
    [Plone](https://plone.org/) is an open-source content management system that is used to create, edit, and manage digital content, like websites, intranets and custom solutions.
    It comes with over 20 years of growth, optimisations, and refinements.
    The result is a system trusted by governments, universities, businesses, and other organisations all over the world.

add-on
    An add-on in Plone extends its functionality.
    It is code that is released as a package to make it easier to install.

    In Volto, an add-on is a JavaScript package.

    In Plone core, an add-on is a Python package.

    -   [Plone core add-ons](https://github.com/collective/awesome-plone#readme)
    -   [Volto add-ons](https://github.com/collective/awesome-volto#readme)
    -   [Add-ons tagged with the trove classifier `Framework :: Plone` on PyPI](https://pypi.org/search/?c=Framework+%3A%3A+Plone)

Markedly Structured Text
MyST
    [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/) is a rich and extensible flavor of Markdown, for authoring Plone Documentation.
    The sample documentation in this scaffold is written in MyST.

Sphinx
    [Sphinx](https://www.sphinx-doc.org/en/master/) is a tool that makes it easy to create intelligent and beautiful documentation.
    It was originally created for Python documentation, and it has excellent facilities for the documentation of software projects in a range of languages.
    It can generate multiple output formats, including HTML and PDF, from a single source.
    This scaffold uses Sphinx to generate documentation in HTML format.

```
