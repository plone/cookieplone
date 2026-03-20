---
myst:
  html_meta:
    "description": "How to use a custom template repository instead of the Cookieplone default."
    "property=og:description": "How to use a custom template repository instead of the Cookieplone default."
    "property=og:title": "Use a custom template repository"
    "keywords": "Cookieplone, custom template, repository, COOKIEPLONE_REPOSITORY, local path, git URL, zip, abbreviation"
---

# Use a custom template repository

Cookieplone supports any template source, not only the default `cookieplone-templates` repository.
You can point it at a local path, a git URL, a zip archive, or a short abbreviation.

## Pass a template on the command line

Pass the template source as the first positional argument:

```console
cookieplone /path/to/my-template
```

```console
cookieplone https://github.com/myorg/my-template.git
```

## Use an abbreviation

Cookieplone supports the abbreviations `gh:`, `gl:`, and `bb:` for GitHub, GitLab, and Bitbucket respectively:

```console
cookieplone gh:myorg/my-template
```

This expands to `https://github.com/myorg/my-template.git`.

## Use a local directory

Pass the path to a local directory that contains a `cookiecutter.json` or `cookieplone.json`:

```console
cookieplone /home/jane/projects/my-template
```

This is the fastest way to develop and test a template—no network request is needed.

## Use a zip archive

Pass a URL to a zip archive:

```console
cookieplone https://example.com/my-template.zip
```

## Pin to a specific tag or branch

Use `--tag` to check out a specific git ref:

```console
cookieplone gh:myorg/my-template --tag v1.2.0
```

## Set the repository with an environment variable

Set `COOKIEPLONE_REPOSITORY` to avoid typing the path on every run:

```console
export COOKIEPLONE_REPOSITORY=/path/to/my-template
cookieplone
```

Set `COOKIEPLONE_REPOSITORY_TAG` to pin the ref:

```console
export COOKIEPLONE_REPOSITORY_TAG=v1.2.0
```

## Related pages

- {doc}`/reference/cli`: `--tag` and positional `template` argument.
- {doc}`/reference/environment-variables`: `COOKIEPLONE_REPOSITORY` and `COOKIEPLONE_REPOSITORY_TAG`.
- {doc}`/concepts/template-repositories`: how Cookieplone discovers and loads templates.
