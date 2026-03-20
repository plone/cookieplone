---
myst:
  html_meta:
    "description": "Solutions to common errors and problems when using cookieplone."
    "property=og:description": "Solutions to common errors and problems when using cookieplone."
    "property=og:title": "Troubleshooting"
    "keywords": "Cookieplone, troubleshooting, errors, problems, debugging, Plone"
---

# Troubleshooting

## "I made a mistake answering a question"

Cookieplone saves your answers to `.cookieplone.json` in the generated project directory.
You have two options:

1. Edit `.cookieplone.json` to fix the incorrect value, then re-run:

   ```console
   cookieplone --answers-file /path/to/.cookieplone.json
   ```

2. Delete the generated directory and run `cookieplone` again from scratch.

See {doc}`how-to-guides/recover-from-mistakes` for a detailed walkthrough.

## "X is not a valid Plone version"

Cookieplone checks that the Plone version is at least 6.0.
Common causes:

- Typing `5.2`: Plone 5.x is not supported.
- Typing `latest`: enter an actual version number such as `6.1.1`.
- Network error—version validation requires internet access to check the latest release.
  Verify your connection and try again.

## "A valid repository could not be found"

This error usually means one of the following:

- No internet connection—Cookieplone downloads templates from GitHub.
- GitHub is unavailable or rate-limiting requests.
- A custom `COOKIEPLONE_REPOSITORY` is set to an invalid URL.

Run with `--verbose` for detailed logs:

```console
cookieplone --verbose
```

See {doc}`reference/environment-variables` for details on `COOKIEPLONE_REPOSITORY`.

## "Hook script failed"

Template hooks run Python scripts before and after generation.
If a hook fails:

- Check the error output above the Cookieplone error message.
- Common cause: missing system dependencies such as `git`, `docker`, or `node`.
- Use `--keep-project-on-failure` to inspect the partial output:

  ```console
  cookieplone --keep-project-on-failure
  ```

See {doc}`how-to-guides/debug-a-failed-generation` for a full debugging workflow.

## "File exists error when re-running with -f"

Re-running Cookieplone with `-f` (`--overwrite-if-exists`) on an existing project merges the new output over the existing directory.
If you see a `FileExistsError`, check that you are using Cookieplone 1.0.0 or later, which contains the fix for [issue #139](https://github.com/plone/Cookieplone/issues/139).

## No module named `cookieplone`

If you installed Cookieplone with `pip` rather than `uvx`, ensure the virtual environment is activated and that the installation completed without errors.
The recommended installation method is `uvx`:

```console
uvx cookieplone
```

## Still stuck

Open an issue at <https://github.com/plone/Cookieplone/issues> with the output of:

```console
cookieplone --info
cookieplone --verbose 2>&1 | head -50
```
