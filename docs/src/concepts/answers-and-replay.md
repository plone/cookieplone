---
myst:
  html_meta:
    "description": "An explanation of the Cookieplone answers file and Cookiecutter replay mechanisms, and when to use each."
    "property=og:description": "An explanation of the Cookieplone answers file and Cookiecutter replay mechanisms, and when to use each."
    "property=og:title": "Answers and replay"
    "keywords": "Cookieplone, answers file, replay, cookieplone.json, __template__, --answers-file, --replay"
---

# Answers and replay

Cookieplone provides two separate mechanisms for reusing previous answers: the **answers file** and the **Cookiecutter replay** system.
They look similar but serve different purposes and are not interchangeable.

## The answers file

Every successful generation writes a file named `.cookieplone.json` into the generated project directory.
This file records the answers the user provided, plus metadata about which template was used.

### Format

```json
{
  "__template__": "project",
  "project_title": "My Plone Site",
  "author_name": "Érico Andrei",
  "author_email": "ericof@plone.org",
  "hostname": "mysite.example.com",
  "plone_version": "6.1.2"
}
```

The `__template__` key records the template name.
All other keys are the field names from the template schema with their resolved values.
Computed fields are not stored—they are re-derived on each run.

### Using the answers file

Pass the file back to Cookieplone with `--answers-file` (or `--answers`):

```console
cookieplone --answers myproject/.cookieplone.json
```

Cookieplone reads the answers as defaults.
If `__template__` is present, it selects the template automatically.
The wizard still runs, allowing you to change any value before regenerating.

Combine with `--no-input` to regenerate without any prompts:

```console
cookieplone --no-input --answers myproject/.cookieplone.json
```

### When to use the answers file

- Re-running Cookieplone to apply template updates to an existing project (use with `-f` or `-s`).
- Pre-filling answers for CI/CD pipelines.
- Sharing a repeatable configuration with a team.
- Recovering from a mistake by editing the file and re-running.

See {doc}`/how-to-guides/use-an-answers-file` and {doc}`/how-to-guides/update-existing-project`.

---

## Cookiecutter replay

Cookiecutter's native replay system captures the full rendered context (including computed fields) and saves it as a JSON file in `~/.cookiecutter_replay/` (or the path configured in `replay_dir`).

### Using replay

Re-run using the most recent replay:

```console
cookieplone --replay
```

Use a specific replay file:

```console
cookieplone --replay-file ~/backups/my-replay.json
```

When a replay file is active, Cookieplone skips the wizard entirely and passes the replay data directly to the file renderer.

### When to use replay

- Reproducing an identical generation for debugging purposes.
- Creating an exact copy of a previously generated project.

---

## Key differences

| Aspect | Answers file (`.cookieplone.json`) | Cookiecutter replay |
|---|---|---|
| Stores computed fields? | No (re-derived each run) | Yes (captures full rendered context) |
| Runs the wizard? | Yes (with pre-filled defaults) | No (skips wizard entirely) |
| Editable for re-runs? | Yes—designed to be edited | Not intended for editing |
| Used in CI? | Yes—combine with `--no-input` | Possible but unusual |
| Stored where? | Inside the generated project | In `~/.cookiecutter_replay/` |
| CLI flag | `--answers-file` / `--answers` | `--replay` / `--replay-file` |

## Related pages

- {doc}`/how-to-guides/use-an-answers-file`: use the answers file to pre-fill prompts.
- {doc}`/how-to-guides/update-existing-project`: re-run Cookieplone on an existing project.
- {doc}`/how-to-guides/automate-with-ci`: use the answers file in CI pipelines.
- {doc}`/how-to-guides/recover-from-mistakes`: edit the answers file to fix a wrong answer.
- {doc}`/reference/cli`: `--answers-file`, `--replay`, and `--replay-file` flags.
