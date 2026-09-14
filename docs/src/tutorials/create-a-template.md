---
myst:
  html_meta:
    "description": "A step-by-step tutorial for building a minimal Cookieplone template repository from scratch."
    "property=og:description": "A step-by-step tutorial for building a minimal Cookieplone template repository from scratch."
    "property=og:title": "Create a template"
    "keywords": "Cookieplone, tutorial, template, template repository, cookieplone-config.json, cookieplone.json, Plone"
---

# Create a template

This tutorial walks you through building a minimal Cookieplone template repository.
By the end, you will have a working template that generates a small project on your machine.

**Prerequisites:**

- [uv](https://docs.astral.sh/uv/) installed.
- Basic familiarity with Jinja2 templating syntax.

## Step 1: Create the repository structure

A template repository needs a repository configuration file at its root and at least one template directory.
You will build this structure:

```text
my-template/
├── cookieplone-config.json            ← repository configuration: lists the templates
└── templates/
    └── myproject/                     ← one template
        ├── cookieplone.json           ← the questions this template asks
        └── {{ cookiecutter.project_slug }}/
            ├── README.md
            └── pyproject.toml
```

Create the directories:

```console
mkdir -p "my-template/templates/myproject/{{ cookiecutter.project_slug }}"
```

Cookieplone renders directory names too: in the generated output, `{{ cookiecutter.project_slug }}` takes the value of the `project_slug` answer.

```{note}
A plain directory is enough for this tutorial.
If you keep your template repository in git, commit your files before you run Cookieplone.
A git repository without any commit fails with an error such as `ValueError: Reference at 'refs/heads/main' does not exist`.
```

## Step 2: Write the repository configuration

The `cookieplone-config.json` file tells Cookieplone which templates the repository provides and how to group them in the selection menu.
Create `my-template/cookieplone-config.json`:

```{literalinclude} ../../_examples/create-a-template/my-template/cookieplone-config.json
:language: json
```

- `version` is the version of the repository configuration format and must be `"1.0"`.
- `templates` maps each template ID to the directory that contains it.
- `groups` organizes templates into categories. Each template must belong to exactly one group.

See {doc}`/reference/repository-config` for every available key.

## Step 3: Write the template questions

Each template has a `cookieplone.json` file that defines the questions asked during generation.
Create `my-template/templates/myproject/cookieplone.json`:

```{literalinclude} ../../_examples/create-a-template/my-template/templates/myproject/cookieplone.json
:language: json
```

- `id` identifies the template.
- `schema` holds the form: its `version` must be `"2.0"`, and each entry in `properties` becomes a question, asked in the order it appears.
- `config` holds generator settings that the user doesn't see. Here, `versions` pins a Python version that the template files can use.

See {doc}`/reference/schema-v2` for every field type and setting.

## Step 4: Write the template files

Cookieplone renders the files inside `{{ cookiecutter.project_slug }}` with Jinja2.
Answers are available as `{{ cookiecutter.<question> }}`, and version pins as `{{ versions.<key> }}`.

Create `my-template/templates/myproject/{{ cookiecutter.project_slug }}/README.md`:

```{literalinclude} ../../_examples/create-a-template/my-template/templates/myproject/{{ cookiecutter.project_slug }}/README.md
:language: markdown
```

Create `my-template/templates/myproject/{{ cookiecutter.project_slug }}/pyproject.toml`:

```{literalinclude} ../../_examples/create-a-template/my-template/templates/myproject/{{ cookiecutter.project_slug }}/pyproject.toml
:language: toml
```

## Step 5: Run your template

Cookieplone reads the template repository from the `COOKIEPLONE_REPOSITORY` environment variable.
From the directory that contains `my-template`, run:

```console
COOKIEPLONE_REPOSITORY=./my-template uvx cookieplone
```

Cookieplone shows a numbered list of categories, then a numbered list of the templates in the chosen category.
Your repository has one of each, so press {kbd}`Enter` twice to select the only category, then the only template.
Answer the questions, or press {kbd}`Enter` to accept each default.
After the last question, Cookieplone shows your answers and asks you to confirm them.

To skip the prompts and accept every default, pass the template ID and `--no-input`:

```console
COOKIEPLONE_REPOSITORY=./my-template uvx cookieplone myproject --no-input
```

## Step 6: Inspect the output

Cookieplone generates the project in the current directory:

```text
my-project/
├── .cookieplone.json
├── pyproject.toml
└── README.md
```

With the default answers, `my-project/README.md` contains:

```{literalinclude} ../../_examples/create-a-template/expected/my-project/README.md
:language: markdown
```

And `my-project/pyproject.toml` contains:

```{literalinclude} ../../_examples/create-a-template/expected/my-project/pyproject.toml
:language: toml
```

`.cookieplone.json` records your answers, so you can generate the project again with the same values.
See {doc}`/how-to-guides/use-an-answers-file`.

## What's next?

- {doc}`/how-to-guides/add-validators-to-your-template`: validate user input on specific fields.
- {doc}`/how-to-guides/add-computed-fields`: derive field values automatically from other fields.
- {doc}`/how-to-guides/use-built-in-filters`: use Cookieplone's built-in Jinja2 filters.
- {doc}`/reference/repository-config`: the complete `cookieplone-config.json` reference.
- {doc}`/reference/schema-v2`: the complete `cookieplone.json` reference.
