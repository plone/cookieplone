---
myst:
  html_meta:
    "description": "How to add input validation to fields in a Cookieplone template."
    "property=og:description": "How to add input validation to fields in a Cookieplone template."
    "property=og:title": "Add validators to your template"
    "keywords": "Cookieplone, validators, template, cookieplone.json, DEFAULT_VALIDATORS, custom validator, ValidationError"
---

# Add validators to your template

A validator checks an answer before Cookieplone accepts it.
In the wizard, a rejected answer shows an error, and Cookieplone asks the question again.
With `--no-input`, Cookieplone validates the values it would use instead, and a rejected value stops the generation.

The examples on this page come from the example repository `docs/_examples/template-features/` in the Cookieplone source tree.

## Use a built-in validator

In your template's `cookieplone.json`, set the `validator` key of a property to the dotted import path of a validator:

```json
{
  "author_email": {
    "type": "string",
    "title": "Author email",
    "default": "jane@example.com",
    "validator": "cookieplone.validators.not_empty"
  }
}
```

Cookieplone provides validators for non-empty values, Python package names, npm package names, Volto add-on names, hostnames, language codes, and Plone and Volto versions.
See {doc}`/reference/validators` for the list.

## Rely on automatic validators

Some field names get a validator without any configuration.
Name a property `python_package_name`, and Cookieplone applies `cookieplone.validators.python_package_name` to it:

```json
{
  "python_package_name": {
    "type": "string",
    "title": "Python package name",
    "default": "collective.example_addon"
  }
}
```

The same happens for properties named `plone_version`, `volto_version`, `hostname`, and `language_code`.
A `validator` key on the property replaces the automatic validator.

## Write a custom validator

1.  Create a Python module in your template's directory, next to its `cookieplone.json`:

    ```{literalinclude} ../../_examples/template-features/my-templates/templates/features/my_validators.py
    :language: python
    ```

    The function receives the answer as a string.
    It returns `True` to accept the answer, or raises `ValidationError` with a message that tells the user what to fix.
    See {ref}`validator-contract` for the complete contract.

2.  Reference the function by its module and function name:

    ```json
    {
      "project_slug": {
        "type": "string",
        "title": "Project slug",
        "default": "example-addon",
        "validator": "my_validators.no_spaces"
      }
    }
    ```

Cookieplone adds the template's directory to the Python import path while it generates the template, so it finds `my_validators` there.
The directory goes at the end of the import path, so pick a module name that no installed package uses.

To share validators between templates or repositories, publish them in a Python package, and install that package next to Cookieplone:

```console
uvx --with my-validators cookieplone
```

## Check the result

With `--no-input`, Cookieplone runs the validators on the defaults and on any value you pass as extra context.
A rejected value stops the generation with the validator's message:

```console
COOKIEPLONE_REPOSITORY=./my-templates uvx cookieplone features "project_slug=example addon" --no-input
```

The error includes `Use hyphens instead of spaces.`

The complete `cookieplone.json` of the example template declares an explicit validator, a custom validator, and a property that gets an automatic validator:

```{literalinclude} ../../_examples/template-features/my-templates/templates/features/cookieplone.json
:language: json
```

## Related pages

- {doc}`/reference/validators`: the validator contract and all built-in validators.
- {doc}`/concepts/validators-and-filters`: how validators and filters differ conceptually.
- {doc}`/how-to-guides/add-a-validator`: add a new built-in validator to Cookieplone itself.
