---
myst:
  html_meta:
    "description": "Write a pytest suite for a downstream Cookieplone repository that uses extends."
    "property=og:description": "Write a pytest suite for a downstream Cookieplone repository that uses extends."
    "property=og:title": "Test an extending repository"
    "keywords": "Cookieplone, extends, pytest, fixtures, downstream, testing"
---

(test-an-extending-repository)=

# Test an extending repository

When your downstream repository declares `extends`, you want a test suite that asserts the merge actually does what you expect: that the right templates win, that your overrides apply, that a baked codebase still produces working output.

Cookieplone ships a pytest plugin that gives you this for free.
As soon as `cookieplone` is a test dependency, a small set of fixtures becomes available through pytest's entry-point mechanism.

## Prerequisites

- A `cookieplone-config.json` at the root of your repository that declares `extends` (see [Extend an upstream template repository](extend-an-upstream-template-repository.md)).
- `cookieplone` installed as a test dependency. With `uv`, add it under `[dependency-groups]` or your test extra in `pyproject.toml`:


  ```toml
  [dependency-groups]
  test = [
      "cookieplone>=2.0",
      "pytest",
  ]
  ```

No conftest changes are required to get started. The fixtures appear automatically.

## The fixtures at a glance

| Fixture | Scope | What it returns |
|---|---|---|
| `downstream_repo_dir` | session | Path to your repository root. Defaults to `Path.cwd()`. |
| `upstream_checkout` | session | Optional git ref override. Defaults to `None`. |
| `upstream_repo_dir` | session | Resolved local path to the immediate upstream. Cloned once per session and cached. |
| `merged_repository_config` | function | The fully-merged `cookieplone-config.json` dict. |
| `template_layers` | function | The `_template_layers` sidecar mapping each template id to its upstream-first layer stack. |
| `bake_from_local` | function | Factory: bake a project from your repository in-process. |
| `bake_in_subprocess` | function | Factory: bake by shelling out to the installed CLI. |

## Assert the merged config

The simplest thing to verify: when your downstream redeclares a template, the downstream definition wins after merging.

```python
def test_project_template_overridden(merged_repository_config):
    project = merged_repository_config["templates"]["project"]
    assert project["title"].startswith("My Org")
```

The fixture returns a fresh deep copy on every call, so a test that mutates the dict cannot leak into another.

## Assert the layer order

`template_layers` exposes the `_template_layers` sidecar as a public contract you can rely on instead of reading internal merge function names.

```python
def test_project_has_one_layer_above_upstream(template_layers):
    layers = template_layers["project"]
    # Upstream-first: layers[-1] is the winning (downstream) layer.
    assert len(layers) == 2
    upstream_repo, upstream_path = layers[0]
    downstream_repo, downstream_path = layers[-1]
    assert "cookieplone-templates" in upstream_repo
```

## Bake a project end-to-end

`bake_from_local` is a factory that runs the same in-process generation pipeline the CLI uses, including extends-aware template-file overlay.

```python
def test_project_generates(bake_from_local):
    result = bake_from_local(
        "project",
        extra_context={
            "title": "Test Site",
            "__folder_name": "test_site",
            "email": "test@example.com",
        },
    )
    assert result.exit_code == 0, result.exception
    assert (result.project_path / "README.md").is_file()
```

The output goes to pytest's per-test `tmp_path` by default.
Pass `output_dir` to redirect.

If you ask for a template id that does not exist in the merged config, `bake_from_local` raises `KeyError` with the available ids listed.

## Bake via the installed CLI

For smoke tests that want to exercise the real entry point (argument parsing, packaging, environment handling), use `bake_in_subprocess`:

```python
def test_smoke_cli(bake_in_subprocess):
    result = bake_in_subprocess(
        "project",                  # template id within the repository
        "title=Smoke Site",
        "__folder_name=smoke",
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
```

The subprocess fixture invokes `python -m cookieplone` with `COOKIEPLONE_REPOSITORY` set to your downstream repository, plus `--no-input` and `-o`. Everything else you pass goes through verbatim.

subprocess tests are an order of magnitude slower than `bake_from_local`. Reach for them when the in-process test would miss the bug.

## Override the resolved upstream

Two override paths exist for development and CI workflows.

### Pin a specific upstream version

Override the `upstream_checkout` fixture in your own `conftest.py`:

```python
import pytest

@pytest.fixture(scope="session")
def upstream_checkout() -> str:
    return "2.1.0"
```

`merged_repository_config`, `template_layers`, and the bake fixtures all honour the pin.

### Use a local upstream checkout

When you are developing against an upstream branch that has not yet been pushed, point pytest at a local checkout instead:

```sh
pytest --cookieplone-upstream-dir=/path/to/local/cookieplone-templates
```

This bypasses cloning entirely; `upstream_repo_dir` yields the supplied path verbatim.

### Keep the clone around for debugging

A failed merge often leaves you wanting to inspect the upstream tree.

```sh
pytest --cookieplone-keep-upstream
```

The clone survives session end so you can `cd` in and look around.

## When the downstream has no extends

The fixtures degrade gracefully:

- `upstream_repo_dir` emits a warning and yields `None`.
- `merged_repository_config` returns the raw downstream config unchanged.
- `template_layers` returns an empty dict.

This lets you write the same assertions whether or not extension is in play. Tests that genuinely require an upstream should guard explicitly:

```python
import pytest

def test_requires_extends(upstream_repo_dir):
    if upstream_repo_dir is None:
        pytest.skip("This test requires the downstream to declare 'extends'.")
    ...
```

## See also

- [Extend an upstream template repository](extend-an-upstream-template-repository.md): how to declare and use `extends` in the first place.
- {ref}`repo-extends`: full reference for the `extends` field and merge rules.
