---
myst:
  html_meta:
    "description": "A step-by-step tutorial for creating your first Plone project using cookieplone."
    "property=og:description": "A step-by-step tutorial for creating your first Plone project using cookieplone."
    "property=og:title": "Create your first Plone project"
    "keywords": "Cookieplone, tutorial, Plone, project, getting started, uvx"
---

# Create your first Plone project

This tutorial walks you through generating a new Plone project with Cookieplone.
By the end, you will have a fully configured project directory ready for development.

**Prerequisites:**

- [uv](https://docs.astral.sh/uv/) installed on your machine.
  Install it with:

  ```console
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- An internet connection—Cookieplone downloads the template repository from GitHub.

## Step 1: Run Cookieplone

Open a terminal in the directory where you want to create your project, then run:

```console
uvx cookieplone
```

Cookieplone downloads the latest `cookieplone-templates` repository and presents a list of available templates.

## Step 2: Choose a template

You see a menu of available templates, for example:

```
? Select a template:
  A Plone Project
  A Plone Backend Add-on
  A Plone Frontend Add-on
```

Use the arrow keys to highlight **A Plone Project** and press {kbd}`Enter`.

## Step 3: Answer the questions

Cookieplone prompts you for project-specific values.
Each prompt shows the field name, a description, and the current default in brackets.
Press {kbd}`Enter` to accept a default, or type a new value.

Common prompts include:

| Prompt | Example value |
|---|---|
| Project title | `My Plone Site` |
| Author name | `Jane Developer` |
| Author email | `jane@example.com` |
| Plone version | `6.1.2` |
| Python package name | `my_plone_site` |

:::{note}
Cookieplone validates your answers as you type.
If you enter an invalid value—for example, a package name with spaces—the prompt stays open until you provide a valid one.
:::

## Step 4: Explore the generated output

When all prompts are answered, Cookieplone generates the project in a new directory named after your package.
The output looks similar to:

```
backend/
  src/
    my_plone_site/
      __init__.py
      configure.zcml
      ...
  setup.cfg
  ...
devops/
  ...
frontend/
  packages/
    ...
Makefile
README.md
```

## Step 5: Verify your setup

Change into the generated directory and inspect the `README.md`:

```console
cd my-plone-site
cat README.md
```

The `README.md` contains the next steps for your specific project, including how to install dependencies and start the development server.

## What's next?

- {doc}`/how-to-guides/use-an-answers-file`: save your answers and reuse them later.
- {doc}`/how-to-guides/update-existing-project`: regenerate after a template update.
- {doc}`/reference/cli`: all Cookieplone command-line options.
