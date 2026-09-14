---
myst:
  html_meta:
    "description": "How to set template answers from the command line with key=value arguments."
    "property=og:description": "How to set template answers from the command line with key=value arguments."
    "property=og:title": "Set answers with extra context"
    "keywords": "Cookieplone, extra context, key=value, answers, command line, no-input, default_context"
---

# Set answers with extra context

Pass `key=value` pairs after the template ID to set answers without writing a file.
Cookieplone calls these pairs extra context.

## Prerequisites

- Cookieplone 2.0, installed or run with `uvx`.
- The names of the fields you want to set.
  A `.cookieplone.json` file from a project you generated lists them, and so does the template's `cookieplone.json`, under `schema.properties`.

## Set an answer

Add one pair per field after the template ID:

```console
uvx cookieplone project title="My Site" author="Jane Doe"
```

Quote values that contain spaces, so your shell passes each pair as one argument.

Cookieplone still asks every question.
Each pair becomes the default of its question, and the answer you type replaces it.

## Generate without questions

Add `--no-input` to use the pairs as answers, and the template defaults for every other field:

```console
uvx cookieplone project title="My Site" author="Jane Doe" --no-input
```

Cookieplone runs the template's validators on each value, and stops with an error when one fails.
See {ref}`validator-contract`.

## Combine pairs with an answers file

Pass the pairs and the answers file together:

```console
uvx cookieplone title="My Renamed Site" --answers-file .cookieplone.json --no-input
```

Cookieplone takes the template from the file's `__template__` key, so you can leave out the template ID.
A pair replaces the value of the same key in the file.

## Which value wins

For each field, Cookieplone uses the first value it finds, in this order:

1. The answer you type at the prompt, in an interactive run.
2. A `key=value` pair on the command line.
3. The answers file.
4. `default_context` in your configuration file.
   See {doc}`/reference/configuration`.
5. The default in the template's `cookieplone.json`.

## Answer no to a yes-or-no question

Every value on the command line is text.
With `--no-input`, Cookieplone treats any value that isn't empty as yes, including `no`, `false`, and `0`.

To answer no, leave the value empty:

```console
uvx cookieplone project initialize_documentation= --no-input
```

In an interactive run, any value that isn't empty makes Yes the default answer.

An answers file keeps JSON types, so `false` in the file answers no:

```json
{
  "__template__": "project",
  "initialize_documentation": false
}
```

## Limits

- A value can't contain `=`.
  Cookieplone stops with a `ValueError`.
  Put such a value in an answers file instead.
- Cookieplone doesn't check a value against the options of a choice question.
  A value that isn't one of the options reaches the template unchanged, so check its spelling against the `const` values in the template's `cookieplone.json`.
- A pair whose key names a computed or constant field replaces that field's value.
  A pair whose key matches no field still reaches the template.
  `.cookieplone.json` records neither, so running again with that file doesn't repeat them.

## What Cookieplone saves

Cookieplone writes `.cookieplone.json` into the generated project.
With `--no-input`, the file records the values you supplied for the template's questions, from pairs, the answers file, or `default_context`.
In an interactive run, it records every answer.

## Related pages

- {doc}`/how-to-guides/use-an-answers-file`: save and reuse answers in a file.
- {doc}`/how-to-guides/automate-with-ci`: generate projects in a pipeline.
- {doc}`/reference/cli`: the `EXTRA_CONTEXT` argument and every option.
