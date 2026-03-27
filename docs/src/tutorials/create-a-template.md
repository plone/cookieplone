---
myst:
  html_meta:
    "description": "A step-by-step tutorial for building a minimal Cookieplone template repository from scratch."
    "property=og:description": "A step-by-step tutorial for building a minimal Cookieplone template repository from scratch."
    "property=og:title": "Create a template"
    "keywords": "Cookieplone, tutorial, template, template repository, cookieplone.json, Plone"
---

# Create a template

This tutorial walks you through building a minimal Cookieplone template repository.
By the end, you will have a working template that you can run locally with `cookieplone`.

**Prerequisites:**

- [uv](https://docs.astral.sh/uv/) installed.
- Basic familiarity with Jinja2 templating syntax.
- Git installed.

## Step 1: Create the repository structure

A Cookieplone template repository requires at minimum a root `cookiecutter.json` and at least one template directory.
Create the following structure:

```console
mkdir my-template
cd my-template
git init
```

Then create these files:

```
my-template/
├── cookiecutter.json          ← root manifest (lists templates)
└── templates/
    └── myproject/             ← one template
        ├── cookieplone.json   ← schema for this template
        └── {{cookiecutter.project_slug}}/
            ├── README.md
            └── pyproject.toml
```

## Step 2: Write the root manifest

The root `cookiecutter.json` tells Cookieplone which templates this repository provides.
Create `cookiecutter.json`:

```json
{
  "templates": {
    "myproject": {
      "path": "./templates/myproject",
      "title": "My project template",
      "description": "A minimal example project."
    }
  }
}
```

## Step 3: Write the template schema

The `cookieplone.json` file inside each template defines the questions asked during generation.
Create `templates/myproject/cookieplone.json`:

```json
{
  "title": "My project template",
  "description": "A minimal example project.",
  "version": "2.0",
  "properties": {
    "project_title": {
      "type": "string",
      "title": "Project title",
      "description": "The human-readable name of your project.",
      "default": "My Project"
    },
    "project_slug": {
      "type": "string",
      "title": "Project slug",
      "description": "Identifier used for the directory name.",
      "default": "my-project"
    },
    "author_name": {
      "type": "string",
      "title": "Author name",
      "default": "Jane Developer"
    },
    "author_email": {
      "type": "string",
      "title": "Author email",
      "default": "jane@example.com"
    }
  }
}
```

## Step 4: Write the template files

Create the Jinja2-templated files that Cookieplone will render.
The directory name `{{cookiecutter.project_slug}}` becomes the generated folder name.

Create `templates/myproject/{{cookiecutter.project_slug}}/README.md`:

```markdown
# {{cookiecutter.project_title}}

Created by {{cookiecutter.author_name}} <{{cookiecutter.author_email}}>.
```

Create `templates/myproject/{{cookiecutter.project_slug}}/pyproject.toml`:

```toml
[project]
name = "{{cookiecutter.project_slug}}"
authors = [
    {name = "{{cookiecutter.author_name}}", email = "{{cookiecutter.author_email}}"},
]
```

## Step 5: Run your template locally

Test your template by pointing Cookieplone at the local directory:

```console
uvx cookieplone /path/to/my-template
```

Cookieplone reads the root `cookiecutter.json`, presents your template in the menu, asks the questions from `cookieplone.json`, and generates output in the current directory.

## Step 6: Inspect the output

After answering the prompts, a new directory appears with your rendered files.
Open `README.md` to confirm the values were substituted correctly.

## What's next?

- {doc}`/how-to-guides/add-validators-to-your-template`: validate user input on specific fields.
- {doc}`/how-to-guides/add-computed-fields`: derive field values automatically from other fields.
- {doc}`/how-to-guides/use-built-in-filters`: use Cookieplone's built-in Jinja2 filters.
- {doc}`/reference/schema-v2`: the complete `cookieplone.json` schema reference.
