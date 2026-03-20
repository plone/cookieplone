---
myst:
  html_meta:
    "description": "Complete reference for all Cookieplone command-line flags and arguments."
    "property=og:description": "Complete reference for all Cookieplone command-line flags and arguments."
    "property=og:title": "CLI reference"
    "keywords": "Cookieplone, CLI, command-line, flags, arguments, reference"
---

# CLI reference

Cookieplone is invoked as:

```console
cookieplone [TEMPLATE] [EXTRA_CONTEXT]... [OPTIONS]
```

Or via `uvx`:

```console
uvx cookieplone [TEMPLATE] [EXTRA_CONTEXT]... [OPTIONS]
```

## Arguments

### `TEMPLATE`

- **Type**: string
- **Default**: _(empty—prompts you to choose)_

The name of a template within the resolved template repository.
When omitted, Cookieplone displays a menu of available templates.

```console
cookieplone project
```

If `COOKIEPLONE_REPOSITORY` is set, the value refers to a template within that repository.

### `EXTRA_CONTEXT`

- **Type**: list of `key=value` strings
- **Default**: _(none)_

Key/value pairs that override individual template fields.
Each item must contain exactly one `=`.

```console
cookieplone project author_name="Érico Andrei" project_title="My Site"
```

Values from `EXTRA_CONTEXT` take precedence over the answers file and template defaults.

## Options

### `-o`, `--output-dir`

- **Type**: path
- **Default**: current working directory

Directory where the generated project is written.

```console
cookieplone -o ~/projects
```

### `--tag`, `--branch`

- **Type**: string
- **Default**: `main`

Git tag or branch of the template repository to use.
Overridden by the `COOKIEPLONE_REPOSITORY_TAG` environment variable.

```console
cookieplone --tag 2024.10.1
```

### `--no-input`

- **Type**: flag (boolean)
- **Default**: `False`

Skip all interactive prompts and use only the values from `cookieplone.json` defaults,
the answers file, and `EXTRA_CONTEXT`.

```console
cookieplone --no-input --answers .cookieplone.json
```

Cannot be combined with `--replay`.

### `-r`, `--replay`

- **Type**: flag (boolean)
- **Default**: `False`

Reuse the most recent Cookiecutter replay file for this template.
This is the Cookiecutter-native replay mechanism, distinct from the Cookieplone answers file.

### `--replay-file`

- **Type**: path
- **Default**: _(none)_

Load a specific Cookiecutter replay file instead of the most recent one.

```console
cookieplone --replay-file ~/backups/my-replay.json
```

### `-s`, `--skip-if-file-exists`

- **Type**: flag (boolean)
- **Default**: `False`

When re-running on an existing project, leave files that already exist untouched.
Use this to add only new files without overwriting customised ones.

### `-f`, `--overwrite-if-exists`

- **Type**: flag (boolean)
- **Default**: `False`

When re-running on an existing project, overwrite files that already exist.
Combine with `-s` to overwrite only files that are not yet present (`-s` takes priority per file).

### `--answers-file`, `--answers`

- **Type**: path
- **Default**: _(none)_

Path to a JSON or YAML file containing pre-filled answers.
The `__template__` key in the file, if present, selects the template automatically.

```console
cookieplone --answers .cookieplone.json
```

See {doc}`/how-to-guides/use-an-answers-file` for the file format.

### `--config-file`

- **Type**: path
- **Default**: _(see {doc}`/reference/configuration`)_

Path to a Cookieplone configuration file.
Overrides the default config file search order.

```console
cookieplone --config-file ~/.my-cookieplone.yaml
```

### `--default-config`

- **Type**: flag (boolean)
- **Default**: `False`

Ignore all user configuration files and use built-in defaults only.

### `--keep-project-on-failure`

- **Type**: flag (boolean)
- **Default**: `False`

Keep the partially generated project directory if a hook script fails.
Useful for diagnosing hook errors.

### `--debug-file`

- **Type**: path
- **Default**: _(none)_

Write `DEBUG`-level log output to the specified file in addition to the console.

```console
cookieplone --debug-file cookieplone-debug.log
```

### `-a`, `--all`

- **Type**: flag (boolean)
- **Default**: `False`

Include hidden templates in the template selection menu.
By default, templates marked `"hidden": true` in the repository's root `cookiecutter.json` are not shown.

```console
cookieplone --all
```

### `-v`, `--verbose`

- **Type**: flag (boolean)
- **Default**: `False`

Print `DEBUG`-level log messages to the console.

### `--info`

- **Type**: flag (boolean)
- **Default**: `False`

Display the resolved repository URL, tag, and password status, then exit.

### `--version`

- **Type**: flag (boolean)
- **Default**: `False`

Display the installed Cookieplone version, then exit.

## Environment variables

Several options can be set through environment variables.
See {doc}`/reference/environment-variables` for the full list.

## Related pages

- {doc}`/reference/environment-variables`: environment variables that affect CLI behaviour.
- {doc}`/reference/configuration`: configuration file format and resolution order.
- {doc}`/how-to-guides/use-an-answers-file`: pre-fill answers to avoid interactive prompts.
- {doc}`/how-to-guides/automate-with-ci`: use Cookieplone in CI pipelines.
