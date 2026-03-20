---
myst:
  html_meta:
    "description": "How to configure Cookieplone using a configuration file and environment variables."
    "property=og:description": "How to configure Cookieplone using a configuration file and environment variables."
    "property=og:title": "Configure Cookieplone"
    "keywords": "Cookieplone, configuration, .Cookieplonerc, config file, default_context, author, email"
---

# Configure Cookieplone

Cookieplone reads a configuration file to set persistent defaults such as your name, email, and preferred template directory.
You can also override configuration with environment variables or command-line flags.

## Create a user configuration file

Create `~/.cookieplonerc` in your home directory.
The file uses YAML format:

```yaml
default_context:
  author_name: Jane Developer
  author_email: jane@example.com
cookiecutters_dir: ~/.cookiecutters/
replay_dir: ~/.cookiecutter_replay/
abbreviations:
  gh: https://github.com/{0}.git
  gl: https://gitlab.com/{0}.git
  bb: https://bitbucket.org/{0}
  myorg: https://github.com/myorg/{0}.git
```

The `default_context` section sets default values for matching field names.
When a template contains a field named `author_name`, Cookieplone pre-fills it with the value from your config.

## Configuration resolution order

Cookieplone looks for configuration in this priority order (highest first):

1. `--config-file` flag (explicit path)
2. `COOKIEPLONE_CONFIG` environment variable
3. `COOKIECUTTER_CONFIG` environment variable
4. `~/.cookieplonerc`
5. `~/.cookiecutterrc`
6. Built-in defaults

The first valid configuration file found is used; the rest are ignored.

## Use a project-specific configuration file

Pass a config file on the command line for a single run:

```console
cookieplone --config-file /path/to/project.yml
```

## Bypass all configuration

Use `--default-config` to ignore any config file and use Cookieplone's built-in defaults:

```console
cookieplone --default-config
```

## Pre-fill author and email from git

If your git config contains `user.name` and `user.email`, Cookieplone reads them and uses them as fallback defaults for `author_name` and `author_email`, without requiring any config file entry.

## Related pages

- {doc}`/reference/configuration`: all recognised configuration keys and their defaults.
- {doc}`/reference/environment-variables`: `COOKIEPLONE_CONFIG` and `COOKIECUTTER_CONFIG`.
- {doc}`/reference/cli`: `--config-file` and `--default-config` flags.
