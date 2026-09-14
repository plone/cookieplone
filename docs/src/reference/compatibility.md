---
myst:
  html_meta:
    "description": "Versions of Python, Plone, Volto, Node.js, and other tools that Cookieplone 2.0 and the official templates support."
    "property=og:description": "Versions of Python, Plone, Volto, Node.js, and other tools that Cookieplone 2.0 and the official templates support."
    "property=og:title": "Compatibility"
    "keywords": "Cookieplone, compatibility, versions, Python, Plone, Volto, Node.js, pnpm, Docker, uv"
---

# Compatibility

This page lists the versions that Cookieplone 2.0 supports, and the versions that the official templates check or use.
The last column of each table names the file each value comes from.
Paths starting with `cookieplone/` are in the Cookieplone repository, and paths starting with `templates/` are in [`cookieplone-templates`](https://github.com/plone/cookieplone-templates).

## Cookieplone

| Requirement | Versions | Source |
|---|---|---|
| Python | 3.10, 3.11, 3.12, 3.13, 3.14 | `pyproject.toml`: `requires-python` and the `Programming Language :: Python` classifiers |
| Python versions in the test suite | 3.10, 3.11, 3.12, 3.13, 3.14, on Linux | `.github/workflows/main.yml`: the test matrix |
| Cookieplone version required by `cookieplone-templates` | 2.0.0b3 or later | `cookieplone-config.json` of `cookieplone-templates`: `config.min_version` |

## Plone and Python

| Plone | Python versions | Source |
|---|---|---|
| 6.0 | 3.10, 3.11, 3.12 | `cookieplone/settings.py`: `PLONE_PYTHON` |
| 6.1 | 3.10, 3.11, 3.12, 3.13 | `cookieplone/settings.py`: `PLONE_PYTHON` |
| 6.2 | 3.10, 3.11, 3.12, 3.13, 3.14 | `cookieplone/settings.py`: `PLONE_PYTHON` |

The `python_versions`, `python_version_earliest`, and `python_version_latest` filters return these Python versions.

| Check | Value | Source |
|---|---|---|
| Lowest Plone version that the `plone_version` validator accepts | 6 | `cookieplone/settings.py`: `PLONE_MIN_VERSION` |

## Volto and Node.js

| Volto | Node.js | Source |
|---|---|---|
| 18 | 22 | `cookieplone/settings.py`: `VOLTO_NODE` |
| 19 | 24 | `cookieplone/settings.py`: `VOLTO_NODE` |
| Any other major version | 24 | `cookieplone/settings.py`: `DEFAULT_NODE` |

The `node_version_for_volto` filter returns these Node.js versions.

| Check | Value | Source |
|---|---|---|
| Lowest Volto version that the `volto_version` validator accepts | 18.0.0-alpha.43 | `cookieplone/settings.py`: `VOLTO_MIN_VERSION` |

## Latest Plone and Volto releases

The `latest_plone` and `latest_volto` filters, which the official templates use for the default Plone and Volto versions, need network access.

| Filter | Asks | On a network error | Source |
|---|---|---|---|
| `latest_plone` | `https://pypi.org/pypi/Plone/json`, with a 10-second timeout | Returns an empty value | `cookieplone/utils/versions.py`, `cookieplone/filters/__init__.py`, `cookieplone/settings.py`: `REQUESTS_TIMEOUT` |
| `latest_volto` | `https://registry.npmjs.org/@plone/volto`, with a 10-second timeout | Returns an empty value | `cookieplone/utils/versions.py`, `cookieplone/filters/__init__.py`, `cookieplone/settings.py`: `REQUESTS_TIMEOUT` |

## Tool checks

Templates check for tools with helpers from `cookieplone.utils.commands`.
When a template doesn't pass its own versions, the helpers use these defaults:

| Check | Default | Source |
|---|---|---|
| Node.js major versions that `check_node_version` accepts | 20, 22, 24 | `cookieplone/settings.py`: `SUPPORTED_NODE_VERSIONS` |
| Lowest Docker version that `check_docker_version` accepts | 20.10 | `cookieplone/settings.py`: `MIN_DOCKER_VERSION` |
| uv and git | Available on the `PATH`, without a version check | `cookieplone/utils/commands/__init__.py`: `check_command_is_available` |

## Official templates

Each template checks for these versions before its first question.
A dash means that the template doesn't check the tool.

| Template | Cookieplone | Node.js | Docker | uv | Source |
|---|---|---|---|---|---|
| `project` | 2.0.0a2 or later | 20, 22, 24 | 26 or later, optional | Required | `templates/projects/monorepo/hooks/pre_prompt.py` |
| `aurora_cmfplone` | 2.0.0a2 or later | 20, 22, 24 | 26 or later, optional | Required | `templates/projects/aurora_cmfplone/hooks/pre_prompt.py` |
| `volto_nick` | 2.0.0a2 or later | 20, 22, 23, 24 | — | — | `templates/projects/volto_nick/hooks/pre_prompt.py` |
| `aurora_nick` | 2.0.0a2 or later | 20, 22, 23, 24 | — | — | `templates/projects/aurora_nick/hooks/pre_prompt.py` |
| `aurora_nick_embedded` | 2.0.0a2 or later | 18, 19, 20, 21, 22, 24 | — | — | `templates/projects/aurora_nick_embedded/hooks/pre_prompt.py` |
| `monorepo_addon` | 2.0.0a2 or later | 20, 22, 24 | 26 or later, optional | Required | `templates/add-ons/monorepo/hooks/pre_prompt.py` |
| `backend_addon` | 2.0.0a2 or later | — | — | Required | `templates/add-ons/backend/hooks/pre_prompt.py` |
| `frontend_addon` | — | 18, 19, 20, 21, 22, 24 | — | — | `templates/add-ons/frontend/hooks/pre_prompt.py` |
| `aurora_addon` | — | 18, 19, 20, 21, 22, 24 | — | — | `templates/add-ons/aurora_addon/hooks/pre_prompt.py` |
| `documentation_starter` | 2.0.0a2 or later | — | — | — | `templates/docs/starter/hooks/pre_prompt.py` |

Templates that check for git require it; `documentation_starter` doesn't check for it.

## Versions pinned by the official templates

`cookieplone-templates` pins these versions in `config.versions`, and its templates read them as `{{ versions.<key> }}`.
They change with each release of `cookieplone-templates`.

| Key | Value | Source |
|---|---|---|
| `backend_python` | 3.14 | `cookieplone-config.json`: `config.versions` |
| `frontend_pnpm` | 10.20.0 | `cookieplone-config.json`: `config.versions` |
| `frontend_aurora_pnpm` | 11.20.0 | `cookieplone-config.json`: `config.versions` |
| `gha_version_node` | 24.x | `cookieplone-config.json`: `config.versions` |
| `devops_db_version` | 18 | `cookieplone-config.json`: `config.versions` |
| `devops_varnish_version` | 8.0 | `cookieplone-config.json`: `config.versions` |
| `devops_traefik_version` | v3.7 | `cookieplone-config.json`: `config.versions` |
| `devops_zeo_version` | 6.0.0 | `cookieplone-config.json`: `config.versions` |
| `tools_pre_commit` | 3.7.1 | `cookieplone-config.json`: `config.versions` |

The `project` template uses pnpm 10.20.0 with Volto 19 or later, and pnpm 9.15.9 with earlier Volto versions (`templates/projects/monorepo/cookieplone.json`: `__version_pnpm`).
