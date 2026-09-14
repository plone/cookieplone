---
myst:
  html_meta:
    "description": "Symptoms, causes, and fixes for failures when you run Cookieplone or develop templates."
    "property=og:description": "Symptoms, causes, and fixes for failures when you run Cookieplone or develop templates."
    "property=og:title": "Troubleshooting"
    "keywords": "Cookieplone, troubleshooting, errors, repository, sanity checks, validation, hooks, Node.js"
---

# Troubleshooting

Each entry starts from what you see, then explains the cause, how to confirm it, and how to fix it.
The entries apply to Cookieplone 2.0.
To change your answers after a generation, see {doc}`how-to-guides/recover-from-mistakes`.

## Run Cookieplone

### `uvx cookieplone` runs an older version

**Symptom**: `uvx cookieplone --version` shows an older version than you expect, or the questions differ from this documentation.

**Cause**: when you installed Cookieplone with `uv tool install`, `uvx cookieplone` runs the installed version.
An installed tool keeps its version until you upgrade it.

**Diagnose**: `uv tool list` shows the installed tools and their versions.

**Fix**: ask for the latest release, or pin a version:

```console
uvx cookieplone@latest
```

For an installed tool, run `uv tool upgrade cookieplone`.
See {doc}`install`.

### "A valid repository for … could not be found"

**Symptom**: Cookieplone stops before the menu, with an error like this:

```text
A valid repository for "/path/to/templates" could not be found in the following locations:
/path/to/templates
```

**Cause**: `COOKIEPLONE_REPOSITORY` points to a folder that doesn't exist, or that has no `cookieplone-config.json` at its root.

**Diagnose**: `cookieplone --info` shows the repository that Cookieplone uses.
Check that `cookieplone-config.json` exists at the root of that folder.

**Fix**: point `COOKIEPLONE_REPOSITORY` to the root of the template repository, or unset it to use [`cookieplone-templates`](https://github.com/plone/cookieplone-templates).

### Cookieplone can't clone the template repository

**Symptom**: Cookieplone stops before the menu with one of these errors, or waits a long time first:

- `Failed to clone '…'.`, followed by the output of git.
- A message that ends with `If this is a private repository, check your authentication.`
- `Cannot clone '…': … Install the required VCS tool and retry.`

**Cause**: Cookieplone can't clone the repository with git.
git may be missing, the network may block access to the repository, or the repository may not exist or may need authentication.

**Diagnose**: clone the repository yourself, in another folder:

```console
git clone https://github.com/plone/cookieplone-templates.git
```

**Fix**: install git, or fix the network access that the clone needs.
To work around a network that blocks Cookieplone, clone the repository yourself, and set `COOKIEPLONE_REPOSITORY` to the clone.
The clone needs `cookieplone-config.json` at its root.

### `This repository requires cookieplone >= …`

**Symptom**: Cookieplone stops with an error like this:

```text
This repository requires cookieplone >= <required version>, but you have <installed version> installed.
Please upgrade:  uvx --no-cache cookieplone@<required version>
```

**Cause**: the template repository sets `config.min_version` to a higher version than the Cookieplone you run.

**Fix**: run the command the message suggests.
For an installed tool, run `uv tool upgrade cookieplone`.

### `We do not have a template named …`

**Symptom**: Cookieplone stops with this message:

```text
We do not have a template named <template ID>.
Available templates are: <template IDs>
Exiting now.
```

**Cause**: the template ID you passed doesn't exist in the repository.

**Fix**: use one of the IDs that the message lists.
{doc}`reference/templates/index` describes the templates of `cookieplone-templates`.

### `Config file … does not exist.`

**Symptom**: Cookieplone stops with `Config file <path> does not exist.`

**Cause**: the file you passed with `--answers-file` doesn't exist.
Cookieplone reads a relative path from the current folder.

**Fix**: check the path to the answers file.

### A tool check fails before the first question

**Symptom**: the template shows the results of its checks, then stops with `Sanity checks failed.`
A failed check shows a message instead of `✓`, such as:

- `NodeJS not found.`
- `Node version is not supported: Got <version>`
- `Command uv is not available.`
- `Command git is not available.`

**Cause**: the `pre_prompt` hook of the template didn't find a tool it requires, or found a version it doesn't support.

**Diagnose**: compare `node --version`, `uv --version`, and `git --version` with the requirements on the template's page in {doc}`reference/templates/index`.

**Fix**: install the missing tool, or switch to a supported Node.js version, for example with nvm.
Then run Cookieplone again.

### "Docker not found." with Docker installed

**Symptom**: the check results show `Docker (optional): Docker not found.`, although Docker Desktop is installed.

**Cause**: the `docker` command isn't on your `PATH`.
On macOS, Docker Desktop can install it in `~/.docker/bin`.

**Diagnose**: run `docker --version`.

**Fix**: add the folder with the `docker` command to your `PATH`.
The Docker check is a warning: generation continues without it.

### "Output directory … already exists."

**Symptom**: Cookieplone stops after the questions with this message:

```text
Output directory '<path>' already exists. Use --overwrite-if-exists or choose a different directory.
```

**Cause**: a folder with the name of the new project already exists in the output directory.

**Fix**: choose another output directory with `-o`, or remove the folder.
To generate into the existing folder, pass `-f`.
With `-f`, the hooks run again on the existing files; see {doc}`concepts/hooks` and {doc}`how-to-guides/update-existing-project`.

### `Default value '' for 'plone_version' fails validation`

**Symptom**: a run with `--no-input` stops with this message:

```text
Default value '' for 'plone_version' fails validation:  is not a valid Plone version.
```

**Cause**: the default Plone version comes from PyPI.
Without network access, the lookup returns an empty value, which the validator rejects.
The default Volto version comes from the npm registry, and fails the same way.

**Fix**: restore network access, or pass the versions on the command line:

```console
uvx cookieplone project plone_version=6.2.2 volto_version=19.4.1 --no-input
```

### "Hook script failed"

**Symptom**: generation stops with a traceback and `Hook script failed (exit status: <number>)`.

**Cause**: a `pre_gen_project` or `post_gen_project` hook of the template failed.
Cookieplone removes the new project folder.

**Diagnose**: read the output above the message.
To inspect the files generated so far, run again with `--keep-project-on-failure`.

**Fix**: fix the cause that the hook reports, such as a missing tool.
See {doc}`how-to-guides/debug-a-failed-generation`.

### `make` reports "No such file or directory" when the path has spaces

**Symptom**: while it generates a `project`, Cookieplone prints a `make` error that names only part of the path of your folder, and continues.

**Cause**: the path of the folder where you run Cookieplone contains spaces.
This issue is open: [issue 208](https://github.com/plone/cookieplone/issues/208).

**Fix**: run Cookieplone in a folder whose path has no spaces.

### `ValueError: dictionary update sequence element #0 has length 3; 2 is required`

**Symptom**: Cookieplone stops with this traceback when you pass `key=value` pairs.

**Cause**: a value contains `=`.

**Fix**: put that answer in an answers file.
See {doc}`how-to-guides/use-extra-context`.

## Develop templates

### "No filter named '…'."

**Symptom**: generation stops with `No filter named '<filter>'.`

**Cause**: the template uses a Cookieplone filter that it doesn't declare.

**Fix**: add the filter, such as `cookieplone.filters.pascal_case`, to `config.extensions` in `cookieplone.json`.
See {doc}`how-to-guides/use-built-in-filters`.

### "Cannot import validator module '…'"

**Symptom**: Cookieplone stops before the first question with `Cannot import validator module '<module>': No module named '<module>'`.

**Cause**: Python can't import the module that a `validator` key names.

**Fix**: put the module next to the template's `cookieplone.json`, or install its package with `uvx --with`.
See {doc}`how-to-guides/add-validators-to-your-template`.

### "Reference at 'refs/heads/…' does not exist"

**Symptom**: generating from a local template repository fails with `ValueError: Reference at 'refs/heads/<branch>' does not exist`.

**Cause**: the repository is a git repository without any commit.

**Fix**: commit the files, or use the folder without git.

### "Default value '…' for '…' fails validation"

**Symptom**: a run with `--no-input` stops with `Default value '<value>' for '<field>' fails validation: <message>`.

**Cause**: the default of a field, or a value you passed, fails the validator of that field.
With `--no-input`, nobody can type another answer.

**Fix**: change the default in `cookieplone.json`, or pass a valid value.
See {ref}`validator-contract`.

## Still stuck

Show the settings that Cookieplone uses:

```console
uvx cookieplone --info
```

Then run the failing command again with `--verbose`, and write the detailed log to a file with `--debug-file`:

```console
uvx cookieplone project --verbose --debug-file cookieplone-debug.log
```

Open an issue at <https://github.com/plone/cookieplone/issues> with both outputs.
