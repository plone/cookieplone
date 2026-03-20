---
myst:
  html_meta:
    "description": "Reference for the Cookieplone configuration file format, recognised keys, and resolution order."
    "property=og:description": "Reference for the Cookieplone configuration file format, recognised keys, and resolution order."
    "property=og:title": "Configuration reference"
    "keywords": "Cookieplone, configuration, Cookieplonerc, default_context, abbreviations, config file"
---

# Configuration reference

Cookieplone reads a YAML (or JSON) configuration file to set persistent defaults.
The file is optional—Cookieplone works without one.

## Resolution order

Cookieplone selects the first configuration source that exists, in this order:

| Priority | Source |
|---|---|
| 1 (highest) | `--config-file <path>` CLI flag |
| 2 | `COOKIEPLONE_CONFIG` environment variable |
| 3 | `COOKIECUTTER_CONFIG` environment variable |
| 4 | `~/.cookieplonerc` |
| 5 | `~/.cookiecutterrc` |
| 6 (lowest) | Built-in defaults |

Pass `--default-config` to skip all user files and use built-in defaults.

## File format

The configuration file is a YAML document with the following top-level keys:

```yaml
cookiecutters_dir: "~/.cookiecutters/"
replay_dir: "~/.cookiecutter_replay/"
default_context:
  author_name: "Érico Andrei"
  author_email: "ericof@plone.org"
abbreviations:
  gh: "https://github.com/{0}.git"
  gl: "https://gitlab.com/{0}.git"
  bb: "https://bitbucket.org/{0}"
  myorg: "https://git.myorg.example.com/{0}.git"
```

## Recognised keys

### `cookiecutters_dir`

- **Type**: path string
- **Default**: `"~/.cookiecutters/"`

Directory where cloned template repositories are cached.

### `replay_dir`

- **Type**: path string
- **Default**: `"~/.cookiecutter_replay/"`

Directory where Cookiecutter replay files are stored when `--replay` is used.

### `default_context`

- **Type**: mapping
- **Default**: `{}`

Key/value pairs that pre-fill template fields of the same name.
Use this to set your name and email so you never need to type them again:

```yaml
default_context:
  author_name: "Érico Andrei"
  author_email: "ericof@plone.org"
  github_username: "ericof"
```

Field-level user input always overrides `default_context`.
`EXTRA_CONTEXT` on the command line overrides both.

### `abbreviations`

- **Type**: mapping
- **Default**: built-in `gh`, `gl`, and `bb` abbreviations

Maps short aliases to full repository URL templates.
The placeholder `{0}` is replaced by the path following the alias.

Built-in abbreviations:

| Alias | Expands to |
|---|---|
| `gh:owner/repo` | `https://github.com/owner/repo.git` |
| `gl:owner/repo` | `https://gitlab.com/owner/repo.git` |
| `bb:owner/repo` | `https://bitbucket.org/owner/repo` |

Add a custom abbreviation:

```yaml
abbreviations:
  gh: "https://github.com/{0}.git"
  gl: "https://gitlab.com/{0}.git"
  bb: "https://bitbucket.org/{0}"
  myorg: "https://git.myorg.example.com/{0}.git"
```

Then use it:

```console
cookieplone myorg:team/templates
```

## Git config fallback

If no `author_name` or `author_email` is found in the configuration file or `default_context`,
Cookieplone reads `user.name` and `user.email` from git config as a fallback.

## Related pages

- {doc}`/reference/environment-variables`: environment variables that override configuration.
- {doc}`/reference/cli`: `--config-file` and `--default-config` flags.
- {doc}`/how-to-guides/configure-cookieplone`: how to create and use a config file.
