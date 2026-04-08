---
myst:
  html_meta:
    "description": "How to run a prerelease version of Cookieplone with uvx, including --prerelease=allow and exact version pinning."
    "property=og:description": "How to run a prerelease version of Cookieplone with uvx, including --prerelease=allow and exact version pinning."
    "property=og:title": "Use a prerelease version of Cookieplone"
    "keywords": "Cookieplone, prerelease, alpha, beta, rc, uvx, uv tool install, PEP 440"
---

# Use a prerelease version of Cookieplone

By default, `uvx cookieplone` installs the latest **stable** release. Prerelease versions (those with an `aN`, `bN`, `rcN`, or `.devN` suffix like `2.0.0a1`) are excluded from automatic resolution.
This matches [PEP 440](https://peps.python.org/pep-0440/) and the `uv` resolver defaults, and it is the right behavior for everyday use: you want the tested, stable version when you scaffold a real project.

When testing a new major version, reproducing a bug against an unreleased fix, or evaluating upcoming features, you need to opt in explicitly.
This guide shows the three supported ways to do that.

## Why `uvx cookieplone` skips prereleases

`uvx cookieplone` is shorthand for `uv tool run cookieplone`.
`uv` resolves the `cookieplone` requirement against PyPI the same way `pip` does, and PEP 440 says that prereleases are only picked when:

1. The requirement specifier itself is a prerelease (for example, `cookieplone==2.0.0a1`), or
2. Only prereleases satisfy the requirement (no stable release matches at all), or
3. The caller explicitly enables prereleases.

With a stable 1.x line published on PyPI alongside a 2.x alpha, condition (1) and (2) do not apply, so stable wins.

## Option 1: Pin the exact prerelease version (recommended)

The clearest and most reproducible option is to pin the version directly in the `uvx` command:

```console
uvx cookieplone@2.0.0a1
```

This tells `uv` to create an ephemeral tool environment with exactly `cookieplone==2.0.0a1`, run it once, and throw the environment away.
Because the version specifier is itself a prerelease, the resolver is happy to install it without any extra flags.

Confirm the running version:

```console
uvx cookieplone@2.0.0a1 --version
```

You should see a line like:

```
Cookieplone 2.0.0a1 from ...
```

## Option 2: Allow prereleases for one run

If you do not want to pin a specific version (for example, because you want the latest alpha whatever its number is), pass `--prerelease=allow` to `uvx`:

```console
uvx --prerelease=allow cookieplone
```

`uv` will resolve `cookieplone` against PyPI with prereleases enabled and pick the most recent version overall, stable or not.
This is a per-invocation flag: the next plain `uvx cookieplone` reverts to the stable-only behavior.

## Option 3: Install the prerelease as a persistent tool

If you expect to run the prerelease repeatedly (for example, while working through a tutorial for the new major version), install it as a persistent `uv` tool:

```console
uv tool install --prerelease=allow cookieplone
```

After that, `cookieplone` is on your `PATH` and every invocation uses the persistent prerelease install.

If you already installed Cookieplone this way from a stable release and want to move to a prerelease, force a reinstall so the cached stable environment is replaced:

```console
uv tool install --reinstall --prerelease=allow cookieplone
```

To upgrade an existing prerelease install to the most recent prerelease on PyPI:

```console
uv tool upgrade --prerelease=allow cookieplone
```

To go back to stable, reinstall without the flag:

```console
uv tool install --reinstall cookieplone
```

## Verify the active version

Regardless of which option you chose, check what you are actually running:

```console
cookieplone --version
```

Or, for the `uvx` ephemeral forms:

```console
uvx cookieplone@2.0.0a1 --version
uvx --prerelease=allow cookieplone --version
```

The output includes the full version string, so you can tell `2.0.0a1` apart from `2.0.0` or `1.x` at a glance.

## When to use a prerelease

- You are following a tutorial or migration guide explicitly written against the upcoming major version.
- You are reproducing a bug against an unreleased fix.
- You are a template author validating your template against the new Cookieplone API surface before general availability.
- You are evaluating new features before they land in a stable release.

For generating a real production project, prefer the stable release.
Prereleases can change their CLI, config format, or filter behavior without notice, and new bugs can appear between alphas.

## Related pages

- {doc}`/reference/cli`: all CLI options recognised by Cookieplone.
- {doc}`/reference/environment-variables`: environment variables that influence Cookieplone behavior.
- [PEP 440: Version Identification and Dependency Specification](https://peps.python.org/pep-0440/): the Python spec that defines prerelease semantics.
