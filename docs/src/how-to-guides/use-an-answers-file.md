---
myst:
  html_meta:
    "description": "How to save and reuse your answers when running cookieplone."
    "property=og:description": "How to save and reuse your answers when running cookieplone."
    "property=og:title": "Use an answers file"
    "keywords": "Cookieplone, answers file, replay, .cookieplone.json, automation"
---

# Use an answers file

Cookieplone saves the answers you give during each generation run to a file called `.cookieplone.json` inside the generated project directory.
You can pass this file back to Cookieplone on subsequent runs to pre-fill the prompts with the same values.

## Load answers from a file

Pass the saved answers file with `--answers-file`:

```console
cookieplone --answers-file path/to/.cookieplone.json
```

Cookieplone reads the answers from the file and uses them as defaults.
You can still change any value at the prompt.

## Skip all prompts using an answers file

Combine `--answers-file` with `--no-input` to run without any prompts:

```console
cookieplone --no-input --answers-file path/to/.cookieplone.json
```

All prompts use the values from the file.
Any field not present in the file uses the template default.

## The `__template__` key

The `.cookieplone.json` file includes a `__template__` key that records which template was used.
When you pass the file with `--answers-file`, Cookieplone uses this key to select the same template automatically, so you are not prompted to choose again.

Example `.cookieplone.json`:

```json
{
  "__template__": "myproject",
  "project_title": "My Plone Site",
  "project_slug": "my-plone-site",
  "author_name": "Jane Developer",
  "author_email": "jane@example.com"
}
```

## Create an answers file manually

You can write an answers file by hand instead of extracting it from a previous run.
The file is plain JSON.
Include only the keys you want to pre-fill; omit the rest to keep template defaults.

## Related pages

- {doc}`/how-to-guides/automate-with-ci`: use answers files in CI pipelines.
- {doc}`/how-to-guides/update-existing-project`: regenerate a project from saved answers.
- {doc}`/concepts/answers-and-replay`: understand the difference between answers files and replay files.
