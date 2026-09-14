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
- **Default**: `gh:plone/cookieplone-templates`, the official [`cookieplone-templates`](https://github.com/plone/cookieplone-templates) repository

Overrides the default template repository.
Accepts any source that Cookieplone supports: a git URL, a local directory path, a zip archive URL, or an abbreviated form (`gh:`, `gl:`, `bb:`).

```console
export COOKIEPLONE_REPOSITORY="gh:myorg/my-templates"
cookieplone
```

## `COOKIEPLONE_REPOSITORY_TAG`

- **Type**: string (git tag or branch name)
- **Default**: `main`

Specifies the git tag or branch to check out when cloning the template repository.
An explicit `--tag`/`--branch` CLI flag takes precedence over this variable.
When neither this variable, `--tag`, nor `COOKIEPLONE_REPOSITORY` is set, and the `main` branch has no `cookieplone-config.json`, Cookieplone checks out `next` instead.

```console
export COOKIEPLONE_REPOSITORY_TAG="next"
cookieplone
```

## `COOKIEPLONE_REPO_PASSWORD`

- **Type**: string
- **Default**: _(none)_

Password of a password-protected zip archive used as the template repository.
Also checked under the name `COOKIECUTTER_REPO_PASSWORD` for compatibility.

Cookieplone doesn't use this variable for git repositories.
It clones them with your git installation, which uses its own credentials, such as an SSH key.

## `COOKIEPLONE_RENDERER`

- **Type**: string (one of `cookiecutter`, `noinput`, `rich`, `stdlib`)
- **Default**: `cookiecutter`

Selects which `tui_forms` renderer the wizard uses for interactive runs.
Overrides the `config.renderer` value in the repository's `cookieplone-config.json`.
The `--no-input` flag always forces the `noinput` renderer regardless of this variable.

```console
export COOKIEPLONE_RENDERER=rich
cookieplone
```

If the renderer name is not registered with `tui_forms`, Cookieplone aborts with an `InvalidConfiguration` error listing the available renderers.

## `COOKIEPLONE_QUIET_MODE_SWITCH`

- **Type**: string
- **Default**: _(not set)_

When set to any non-empty value, silences the messages that Cookieplone prints to the console.
It doesn't change the wizard.

Cookieplone sets this variable itself while it generates sub-templates, so that their messages don't clutter the main run, and removes it afterward.

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

When set, even to an empty value, the `use_prerelease_versions` filter returns `Yes` instead of `No`.
Templates that pass that result to the `latest_plone` and `latest_volto` filters then include prerelease versions.

```console
export USE_PRERELEASE=1
cookieplone
```

## Related pages

- {doc}`/reference/configuration`: configuration file format and full resolution order.
- {doc}`/reference/cli`: CLI flags that override environment variables.
- {doc}`/how-to-guides/use-a-custom-template-repository`: use a non-default template repository.
- {doc}`/how-to-guides/automate-with-ci`: using environment variables in CI pipelines.
