---
myst:
  html_meta:
    "description": "Generate a Plone 6 project with Cookieplone, answer its questions, explore the result, and start the project."
    "property=og:description": "Generate a Plone 6 project with Cookieplone, answer its questions, explore the result, and start the project."
    "property=og:title": "Create your first Plone project"
    "keywords": "Cookieplone, tutorial, Plone 6, project, Volto, uvx, getting started"
---

# Create your first Plone project

In this tutorial, you generate a Plone 6 project with Cookieplone, look at what it created, and start the project.

## Before you start

You need:

- uv and git, as {doc}`/install` describes.
- Node.js 20, 22, or 24, which the `project` template checks for.
- An internet connection.
  Cookieplone downloads the templates, and the template looks up the latest Plone and Volto releases.

Docker is optional for this tutorial.

## Step 1: Start Cookieplone

Open a terminal in the folder where you want to create the project, and run:

```console
uvx cookieplone
```

Cookieplone downloads [`cookieplone-templates`](https://github.com/plone/cookieplone-templates), and lists its categories:

```text
1  Projects
    Generate new Plone project
2  Add-ons
    Generate add-on extending Plone
3  Documentation
    Generate documentation for Plone projects or add-ons

Select a category [1/2/3] (1):
```

Press {kbd}`Enter` to choose **Projects**.

## Step 2: Choose the template

Cookieplone lists the templates of the category:

```text
1  Plone 6 Project
    Create a new Plone 6 project (Volto or Classic UI)
2  Plone Aurora (alpha) with Plone backend
    Create a Plone Aurora project with a Python CMFPlone backend
3  Plone Volto using Nick as backend
    Create a Plone Volto project using Nick as backend
4  Plone Aurora (alpha) using Nick as backend
    Plone Aurora (alpha) using Nick as backend
5  Plone Aurora (alpha) using Nick as an embedded library (experimental)
    Plone Aurora (alpha) using Nick as an embedded library (experimental)

Select a template [1/2/3/4/5] (1):
```

Press {kbd}`Enter` to choose **Plone 6 Project**.

Before its first question, the template checks your computer for the tools it needs:

```text
Creating a new Plone Project

Sanity check results:

  - Cookieplone: ✓
  - uv: ✓
  - Node: ✓
  - git: ✓
  - Docker (optional): ✓
```

If a required check fails, the template stops.
Install the missing tool, and run `uvx cookieplone` again.

## Step 3: Answer the questions

Each question shows its position, its title, a description, and the default answer:

```text
[1/18] Project Title
Human-readable name for the project, used in README and documentation.

Default [Project Title]:
```

Type `My Plone Site`, and press {kbd}`Enter`.

For each of the next questions, press {kbd}`Enter` to accept the default, with two exceptions:

- For **Author**, type your name.
- For **Author E-mail**, type your email address.

Cookieplone pre-fills both from your git configuration, so their defaults may already be right.

As you answer, notice that:

- Many defaults come from earlier answers.
  After you type `My Plone Site`, **Project Slug** defaults to `my-plone-site`, and **Python Package Name** to `my.plone.site`.
- **Plone Version** and **Volto Version** default to the latest releases.
- Yes-or-no questions show `Confirm (Y/n):`, where the capital letter is the default.
- Questions with choices, such as **Language**, show a numbered list: type a number, or press {kbd}`Enter` for the default.
- The total changes from 18 to 20 when you answer yes to **Use Volto as frontend?**, because Cookieplone adds two questions: **Volto Version**, and the name of the project's Volto add-on.
- Type `<` to go back to the previous question.

{doc}`/reference/templates/project` lists every question with its default.

## Step 4: Review your answers

After the last question, Cookieplone shows all your answers:

```text
Review your answers

  Project Title                                       My Plone Site
  Project Description                                 A new project using Plone 6.
  Project Slug (Used for repository id)               my-plone-site
  Project URL (without protocol)                      my-plone-site.example.com
  Author                                              Jane Doe
  Author E-mail                                       jane@example.com
  Python Package Name                                 my.plone.site
  Should we use prerelease versions?                  No
  Plone Version                                       6.2.2
  Use Volto as frontend?                              Yes
  Volto Version                                       19.4.1
  Volto Addon Name                                    volto-my-plone-site
  Language                                            English
  ...

Proceed? [Y/n]:
```

Press {kbd}`Enter` to generate the project.
To change an answer, type `n`: Cookieplone asks the questions again, with your answers as defaults.

## Step 5: Watch the generation

Cookieplone generates the project, and lists each step:

```text
 -> Setup Backend
 -> Setup Frontend
 -> Generate documentation scaffold
 -> Setup Cache
 -> Setup Project Settings
 -> Setup VSCode configuration
 -> Setup GitHub CI
 ...
 -> Format backend code
 -> Format frontend code
 ...
 -> Initialize Git repository
```

A line that starts with `Ignoring` names a step that your answers turned off.
When it finishes, Cookieplone shows a summary with the title of your project.

## Step 6: Explore the project

Change into the new folder:

```console
cd my-plone-site
```

The project has these files and folders:

% tree:begin

```text
my-plone-site/
├── .cookieplone.json
├── .editorconfig
├── .github/
├── .gitignore
├── .readthedocs.yml
├── .vscode/
├── backend/
├── CHANGELOG.md
├── devops/
├── docker-compose.yml
├── docs/
├── frontend/
├── Makefile
├── news/
├── README.md
├── repository.toml
├── towncrier.toml
└── version.txt
```

% tree:end

- `backend` holds the Plone backend, with your Python package `my.plone.site` in `backend/src`.
- `frontend` holds the Volto project, with your add-on in `frontend/packages/volto-my-plone-site`.
- `devops` holds the Docker, Ansible, and deployment files.
- `docs` holds a documentation scaffold.
- `.cookieplone.json` records your answers.
  See {doc}`/how-to-guides/use-an-answers-file`.

Cookieplone created a git repository and staged all the files, but didn't commit them.
Make the first commit:

```console
git commit -m "Create project with Cookieplone"
```

## Step 7: Start the project

The generated `README.md` explains how to work on the project, and lists its prerequisites.
Install the backend and the frontend, create a Plone site, and start the backend:

```console
make install
make backend-create-site
make backend-start
```

The backend runs at `http://localhost:8080`.
In a second terminal, from the same folder, start the frontend:

```console
make frontend-start
```

Open `http://localhost:3000` in your browser to see your Plone site.

## Generate the same project without questions

You can give Cookieplone all your answers up front, and skip the questions.
Save these answers as `answers.json`:

```{literalinclude} ../../_examples/first-project/answers.json
:language: json
```

Then run Cookieplone with `--no-input`:

```console
uvx cookieplone --answers-file answers.json --no-input
```

Cookieplone uses the template from `__template__`, your answers, and the default of every other question.
See {doc}`/how-to-guides/automate-with-ci`.

## What's next

- {doc}`/reference/templates/project`: every question of the `project` template, and what your answers change.
- {doc}`/how-to-guides/update-existing-project`: generate the project again after a template update.
- {doc}`/how-to-guides/use-extra-context`: set answers on the command line.
