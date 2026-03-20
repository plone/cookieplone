---
myst:
  html_meta:
    "description": "How to run Cookieplone non-interactively in continuous integration pipelines."
    "property=og:description": "How to run Cookieplone non-interactively in continuous integration pipelines."
    "property=og:title": "Automate with CI"
    "keywords": "Cookieplone, CI, continuous integration, automation, no-input, answers file"
---

# Automate with CI

You can run Cookieplone in a continuous integration (CI) pipeline without any interactive prompts.
Use `--no-input` together with an answers file to provide all values up front.

## Basic non-interactive run

The `--no-input` flag skips all prompts and uses template defaults for any value not supplied:

```console
cookieplone --no-input
```

To supply specific values, combine it with `--answers-file`:

```console
cookieplone --no-input --answers-file answers.json
```

## Example answers file

Create `answers.json` in your repository:

```json
{
  "__template__": "myproject",
  "project_title": "My Plone Site",
  "project_slug": "my-plone-site",
  "author_name": "CI Bot",
  "author_email": "ci@example.com",
  "plone_version": "6.1.2"
}
```

## Example GitHub Actions workflow

```yaml
name: Generate project

on:
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Generate project
        run: |
          uvx cookieplone \
            --no-input \
            --answers-file answers.json \
            --output-dir /tmp/generated
```

## Specifying a fixed template version

Pin the template repository to a specific tag to ensure reproducible builds:

```console
cookieplone --no-input --tag v1.2.3 --answers-file answers.json
```

Or set the tag with an environment variable:

```console
COOKIEPLONE_REPOSITORY_TAG=v1.2.3 cookieplone --no-input --answers-file answers.json
```

## Related pages

- {doc}`/how-to-guides/use-an-answers-file`: create and manage answers files.
- {doc}`/reference/cli`: all CLI flags.
- {doc}`/reference/environment-variables`: all supported environment variables.
