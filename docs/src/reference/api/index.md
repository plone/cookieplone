---
myst:
  html_meta:
    "description": "Reference for the Cookieplone Python API that template hooks use: sub-templates, post-generation actions, and helpers."
    "property=og:description": "Reference for the Cookieplone Python API that template hooks use: sub-templates, post-generation actions, and helpers."
    "property=og:title": "Python API reference"
    "keywords": "Cookieplone, API, Python, hooks, run_subtemplates, run_post_gen_actions, generate_subtemplate"
---

# Python API reference

These modules are the Python API that template hooks use.
Cookieplone runs a template's hooks with the Python interpreter that runs Cookieplone itself, so a hook can import them.

Validators and filters have their own pages: {doc}`/reference/validators` and {doc}`/reference/filters`.

## Sub-templates

```{eval-rst}
.. automodule:: cookieplone.utils.subtemplates
   :members: run_subtemplates, SubtemplateHandler
```

## Post-generation actions

```{eval-rst}
.. automodule:: cookieplone.utils.post_gen
   :members:
```

## Generator

```{eval-rst}
.. autofunction:: cookieplone.generator.generate_subtemplate
```

## Git

```{eval-rst}
.. automodule:: cookieplone.utils.git
   :members:
```

## Plone

```{eval-rst}
.. automodule:: cookieplone.utils.plone
   :members:
```

## npm

```{eval-rst}
.. automodule:: cookieplone.utils.npm
   :members:
```

## Related pages

- {doc}`/how-to-guides/call-subtemplates-from-a-hook`: use `run_subtemplates` in a post-generation hook.
- {doc}`/how-to-guides/run-post-gen-actions`: use `run_post_gen_actions` and its handlers.
- {doc}`/concepts/subtemplates`: how sub-templates are declared and run.
