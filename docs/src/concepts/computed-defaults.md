---
myst:
  html_meta:
    "description": "An explanation of how Cookieplone evaluates computed field defaults using Jinja2 expressions."
    "property=og:description": "An explanation of how Cookieplone evaluates computed field defaults using Jinja2 expressions."
    "property=og:title": "Computed defaults"
    "keywords": "Cookieplone, computed defaults, Jinja2, format computed, cookieplone.json, evaluation order"
---

# Computed defaults

Computed fields derive their values from Jinja2 expressions evaluated after the user has answered all interactive prompts.
They never appear in the wizard.

## How evaluation works

After the wizard collects the user's answers, Cookieplone evaluates every field marked `"format": "computed"` in the order they appear in `properties`.

Each expression is rendered as a Jinja2 template with the current context—including all fields that have been resolved so far.

```json
{
  "properties": {
    "project_slug": {
      "type": "string",
      "title": "Project slug",
      "default": "my-project"
    },
    "package_name": {
      "type": "string",
      "format": "computed",
      "default": "{{ cookiecutter.project_slug | replace('-', '_') }}"
    },
    "module_path": {
      "type": "string",
      "format": "computed",
      "default": "src/{{ cookiecutter.package_name }}"
    }
  }
}
```

In this example:

1. `project_slug` is answered by the user (value: `my-project`).
2. `package_name` is computed from `project_slug` (result: `my_project`).
3. `module_path` is computed from `package_name` (result: `src/my_project`).

## Evaluation order

Properties are evaluated in the order they appear in the `properties` object.
A computed field can reference only fields that appear **earlier** in `properties`.

Referencing a field that appears later produces an empty string or raises a Jinja2 error,
because that field has not been resolved yet when the expression is evaluated.

## Available context

Inside a computed expression, the Jinja2 context includes:

- All user-answered fields resolved so far.
- All computed fields resolved so far.
- All built-in Cookieplone filters (see {doc}`/reference/filters`).
- The `cookiecutter` namespace prefix (for example, `cookiecutter.project_slug`).

## Constant fields

Fields with `"format": "constant"` are similar to computed fields but simpler.
Their `default` is a literal string—not a Jinja2 expression—and it never changes regardless of user input.

```json
{
  "schema_version": {
    "type": "string",
    "format": "constant",
    "default": "2.0"
  }
}
```

Use constant fields to embed fixed metadata (schema versions, generator signatures) into every generated project.

## Computed fields in --no-input mode

When `--no-input` is set, interactive fields use their schema defaults instead of prompting the user.
Computed fields still evaluate their Jinja2 expressions against those defaults.
The evaluation order and rules are identical.

## Why this design

Cookieplone inherits the Jinja2-in-defaults mechanism from Cookiecutter.
Keeping computed fields in the schema (rather than in hooks) means:

- The derivation logic is visible and auditable in one place.
- No Python knowledge is required to add derived fields.
- The wizard can show users the interactive fields without exposing implementation details.

## Related pages

- {doc}`/reference/schema-v2`: the `format: computed` field specification.
- {doc}`/reference/filters`: all built-in filters usable in computed expressions.
- {doc}`/how-to-guides/add-computed-fields`: how to add computed fields to a template.
