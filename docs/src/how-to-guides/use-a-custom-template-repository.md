---
myst:
  html_meta:
    "description": "How to use a custom template repository instead of the Cookieplone default."
    "property=og:description": "How to use a custom template repository instead of the Cookieplone default."
    "property=og:title": "Use a custom template repository"
    "keywords": "Cookieplone, custom template, repository, COOKIEPLONE_REPOSITORY, template ID, local path, git URL, zip, abbreviation"
---

# Use a custom template repository

Cookieplone generates projects from [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) by default.
To use another template repository, set the `COOKIEPLONE_REPOSITORY` environment variable to a local directory, a git URL, an abbreviation, or a zip archive.

## Set the repository

Set `COOKIEPLONE_REPOSITORY` for a single run:

```console
COOKIEPLONE_REPOSITORY=gh:myorg/my-templates uvx cookieplone
```

Or export it for every run in the current shell:

```console
export COOKIEPLONE_REPOSITORY=gh:myorg/my-templates
uvx cookieplone
```

Cookieplone shows the menu of the repository's templates.
To skip the menu, pass the ID of a template from the repository's `cookieplone-config.json`:

```console
COOKIEPLONE_REPOSITORY=gh:myorg/my-templates uvx cookieplone backend_addon
```

```{note}
The positional argument of `cookieplone` is always a template ID.
Cookieplone doesn't accept a repository path or URL there: set `COOKIEPLONE_REPOSITORY` instead.
```

## Use a local directory

Set `COOKIEPLONE_REPOSITORY` to the directory that contains `cookieplone-config.json`.
A relative path works:

```console
COOKIEPLONE_REPOSITORY=./my-templates uvx cookieplone
```

Cookieplone reads the files directly from the directory, which makes this the fastest way to develop and test templates.
The directory can be a plain directory or a git repository.
A git repository needs at least one commit.

## Use a git repository or an abbreviation

HTTPS and SSH git URLs both work:

```console
COOKIEPLONE_REPOSITORY=https://github.com/myorg/my-templates.git uvx cookieplone
```

The abbreviations `gh:`, `gl:`, and `bb:` stand for GitHub, GitLab, and Bitbucket.
For example, `gh:myorg/my-templates` expands to `https://github.com/myorg/my-templates.git`.

Cookieplone clones git repositories with your git installation, so a private repository works with the credentials that git already uses, such as an SSH key.

## Use a zip archive

Set `COOKIEPLONE_REPOSITORY` to the web address or the path of a zip archive:

```console
COOKIEPLONE_REPOSITORY=https://example.com/my-templates.zip uvx cookieplone
```

For a password-protected archive, set `COOKIEPLONE_REPO_PASSWORD` to its password.

## Pin a tag or branch

For a git repository, check out a tag or branch with `--tag`, or its alias `--branch`:

```console
COOKIEPLONE_REPOSITORY=gh:myorg/my-templates uvx cookieplone --tag v1.2.0
```

Or set `COOKIEPLONE_REPOSITORY_TAG`:

```console
export COOKIEPLONE_REPOSITORY_TAG=v1.2.0
```

`--tag` takes precedence over the variable.
Without either, Cookieplone checks out `main`, so set one of them when your repository's default branch has another name.
Cookieplone ignores the tag for local directories and zip archives.

To check which repository and tag Cookieplone resolves, run:

```console
uvx cookieplone --info
```

## Related pages

- {doc}`/reference/cli`: the `TEMPLATE` argument and the `--tag` option.
- {doc}`/reference/environment-variables`: `COOKIEPLONE_REPOSITORY`, `COOKIEPLONE_REPOSITORY_TAG`, and `COOKIEPLONE_REPO_PASSWORD`.
- {doc}`/concepts/template-repositories`: how Cookieplone discovers and loads templates.
- {doc}`/tutorials/create-a-template`: build a local template repository from scratch.
