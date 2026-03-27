---
myst:
  html_meta:
    "description": "How to re-run Cookieplone on an existing project to apply template updates."
    "property=og:description": "How to re-run Cookieplone on an existing project to apply template updates."
    "property=og:title": "Update an existing project"
    "keywords": "Cookieplone, update, re-run, overwrite, answers file, existing project"
---

# Update an existing project

When a template releases updates, you can re-run Cookieplone on your existing project to apply the changes.

## Prerequisites

You need the `.cookieplone.json` answers file from the original generation.
It is located inside your generated project directory.
If you do not have it, create one manually—see {doc}`/how-to-guides/use-an-answers-file`.

## Overwrite existing files

Use `--overwrite-if-exists` (short: `-f`) to allow Cookieplone to write into an existing output directory:

```console
cookieplone -f --answers-file /path/to/project/.cookieplone.json
```

Cookieplone regenerates all template files in place.
Files that exist in the template but not in your project are added.
Files that exist in your project but not in the template are left untouched.

## Preserve files that you have customised

Use `--skip-if-file-exists` (short: `-s`) to protect files you have modified from being overwritten:

```console
cookieplone -f -s --answers-file /path/to/project/.cookieplone.json
```

With this flag, Cookieplone skips any file that already exists on disk, adding only new files from the template.

## Combine with a specific template tag

Pin the update to a specific template release:

```console
cookieplone -f --tag v2.0.0 --answers-file /path/to/project/.cookieplone.json
```

## Review the changes before committing

After running Cookieplone, review the diff with git before committing:

```console
cd /path/to/project
git diff
git add -p
```

## Related pages

- {doc}`/how-to-guides/use-an-answers-file`: create and manage answers files.
- {doc}`/how-to-guides/recover-from-mistakes`: undo a failed update.
- {doc}`/reference/cli`: `--overwrite-if-exists` and `--skip-if-file-exists` flags.
