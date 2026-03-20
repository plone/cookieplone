---
myst:
  html_meta:
    "description": "How to fix mistakes made when answering Cookieplone prompts."
    "property=og:description": "How to fix mistakes made when answering Cookieplone prompts."
    "property=og:title": "Recover from mistakes"
    "keywords": "Cookieplone, mistakes, fix answers, regenerate, .cookieplone.json"
---

# Recover from mistakes

If you made a mistake answering a prompt, you have two options: edit the answers file and regenerate, or delete the output and start over.

## Option 1: Edit the answers file and regenerate

Cookieplone writes `.cookieplone.json` into the generated project directory after each run.

1. Open the file in a text editor:

   ```console
   nano /path/to/generated-project/.cookieplone.json
   ```

2. Correct the wrong values, then save.

3. Re-run Cookieplone with the corrected file and the overwrite flag:

   ```console
   Cookieplone -f --answers-file /path/to/generated-project/.cookieplone.json
   ```

   Cookieplone regenerates the project with the corrected values.

4. Review the changes with git before committing:

   ```console
   cd /path/to/generated-project
   git diff
   ```

## Option 2: Delete and regenerate

If the project directory has no committed work worth keeping, delete it and start fresh:

```console
rm -rf /path/to/generated-project
cookieplone
```

## Related pages

- {doc}`/how-to-guides/use-an-answers-file`: use saved answers to avoid re-typing.
- {doc}`/how-to-guides/update-existing-project`: the full update workflow.
