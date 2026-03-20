---
myst:
  html_meta:
    "description": "How to debug a failed Cookieplone generation run using verbose logging and debug options."
    "property=og:description": "How to debug a failed Cookieplone generation run using verbose logging and debug options."
    "property=og:title": "Debug a failed generation"
    "keywords": "Cookieplone, debug, verbose, logging, hook failure, keep-project-on-failure"
---

# Debug a failed generation

When Cookieplone fails, the error message often points to the root cause.
If it does not, these tools give you more information.

## Enable verbose output

Add `--verbose` (short: `-v`) to see detailed progress logs:

```console
cookieplone --verbose
```

This prints each step of the generation pipeline, including which hook scripts are being executed and which files are being rendered.

## Write logs to a file

Use `--debug-file` to capture the full debug output to a file for later inspection:

```console
cookieplone --debug-file /tmp/cookieplone-debug.log
```

Open the file with any text editor after the run.

## Inspect the partial output after a hook failure

When a post-generation hook fails, Cookieplone normally deletes the partially generated project.
Use `--keep-project-on-failure` to prevent deletion:

```console
cookieplone --keep-project-on-failure
```

You can then inspect the partial output to understand which files were generated before the failure and whether any file content caused the hook to fail.

## Read hook error output

Hook error messages appear above the Cookieplone error message in the terminal.
Look for lines starting with `Traceback` or containing the hook file name (for example `pre_prompt` or `post_gen_project`).

Common hook failure causes:

- Missing system dependencies such as `git`, `docker`, or `node`.
- A `pre_prompt` hook that rejects the current environment.
- A `post_gen_project` hook that runs an external command that is not installed.

## Check your environment

Run the following to confirm Cookieplone and its dependencies are installed correctly:

```console
cookieplone --info
```

## Related pages

- {doc}`/reference/cli`: `--verbose`, `--debug-file`, and `--keep-project-on-failure` flags.
- {doc}`/troubleshooting`: common error messages and their solutions.
