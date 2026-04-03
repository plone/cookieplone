---
myst:
  html_meta:
    "description": "All environment variables recognised by Cookieplone, with their type, default, and effect."
    "property=og:description": "All environment variables recognised by Cookieplone, with their type, default, and effect."
    "property=og:title": "Environment variables reference"
    "keywords": "Cookieplone, environment variables, COOKIEPLONE_REPOSITORY, COOKIEPLONE_CONFIG, reference"
---

# Environment variables reference

Cookieplone reads these environment variables at startup.
CLI flags take precedence over environment variables where both exist.

## `COOKIEPLONE_REPOSITORY`

- **Type**: string (URL, local path, or abbreviation)
- **Default**: `gh:plone/cookieplone-templates`

Overrides the default template repository.
Accepts any source that Cookieplone supports: a git URL, a local directory path, a zip archive URL, or an abbreviated form (`gh:`, `gl:`, `bb:`).

```console
export COOKIEPLONE_REPOSITORY="gh:myorg/my-templates"
cookieplone
```

## `COOKIEPLONE_REPOSITORY_TAG`

- **Type**: string (git tag or branch name)
- **Default**: `next`

Specifies the git tag or branch to check out when cloning the template repository.
Overrides the `--tag`/`--branch` CLI flag.

```console
export COOKIEPLONE_REPOSITORY_TAG="2024.10.1"
cookieplone
```

## `COOKIEPLONE_REPO_PASSWORD`

- **Type**: string
- **Default**: _(none)_

Password or token used to authenticate when cloning a private template repository.
Also checked under the name `COOKIECUTTER_REPO_PASSWORD` for compatibility.

Set this variable rather than embedding credentials in the repository URL.

## `COOKIEPLONE_QUIET_MODE_SWITCH`

- **Type**: string
- **Default**: _(not set)_

When set to any non-empty value, suppresses the interactive (Textual User Interface) wizard
and falls back to a plain text prompt.
Use this in headless environments where a terminal User Interface (TUI) cannot render correctly.

```console
export COOKIEPLONE_QUIET_MODE_SWITCH=1
cookieplone
```

## `COOKIEPLONE_CONFIG`

- **Type**: path string
- **Default**: _(none)_

Path to a Cookieplone configuration file.
Takes precedence over `COOKIECUTTER_CONFIG` and the default file search (`~/.cookieplonerc`, `~/.cookiecutterrc`).
Overridden by the `--config-file` CLI flag.

```console
export COOKIEPLONE_CONFIG="/etc/cookieplone/config.yaml"
cookieplone
```

## `COOKIECUTTER_CONFIG`

- **Type**: path string
- **Default**: _(none)_

Path to a Cookiecutter-compatible configuration file.
Used when `COOKIEPLONE_CONFIG` is not set.
Overridden by both `COOKIEPLONE_CONFIG` and `--config-file`.

## `USE_PRERELEASE`

- **Type**: flag (presence)
- **Default**: _(not set)_

When set to any non-empty value, the `use_prerelease_versions`, `latest_plone`, and `latest_volto` filters include pre-release versions in their results.

```console
export USE_PRERELEASE=1
cookieplone
```

## Related pages

- {doc}`/reference/configuration`: configuration file format and full resolution order.
- {doc}`/reference/cli`: CLI flags that override environment variables.
- {doc}`/how-to-guides/use-a-custom-template-repository`: use a non-default template repository.
- {doc}`/how-to-guides/automate-with-ci`: using environment variables in CI pipelines.
