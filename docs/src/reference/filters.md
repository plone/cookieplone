---
myst:
  html_meta:
    "description": "All built-in Jinja2 filters provided by Cookieplone, with signatures and examples."
    "property=og:description": "All built-in Jinja2 filters provided by Cookieplone, with signatures and examples."
    "property=og:title": "Filters reference"
    "keywords": "Cookieplone, filters, Jinja2, reference, package_name, pascal_case, latest_plone"
---

# Filters reference

Cookieplone registers these Jinja2 filters automatically for every template.
Use them with the `|` operator in template files, computed field defaults, and directory names.

All filters are defined in `cookieplone/filters/__init__.py` using the `@simple_filter` decorator from `cookiecutter.utils`.

---

## `package_name`

**Signature**: `package_name(v: str) -> str`

Returns the last segment of a dotted Python package name.

| Input | Output |
|---|---|
| `"collective.myaddon"` | `"myaddon"` |
| `"plone.app.content"` | `"content"` |
| `"myaddon"` | `"myaddon"` |

---

## `package_namespace`

**Signature**: `package_namespace(v: str) -> str`

Returns all segments of a dotted package name except the last one.
Returns an empty string when there is no namespace.

| Input | Output |
|---|---|
| `"collective.myaddon"` | `"collective"` |
| `"plone.app.content"` | `"plone.app"` |
| `"myaddon"` | `""` |

---

## `package_namespaces`

**Signature**: `package_namespaces(v: str) -> str`

Returns a comma-separated string of all namespace prefixes formatted for use in `setup.py`.

| Input | Output |
|---|---|
| `"collective.myaddon"` | `'"collective"'` |
| `"plone.app.content"` | `'"plone", "plone.app"'` |
| `"myaddon"` | `""` |

---

## `package_namespace_path`

**Signature**: `package_namespace_path(v: str) -> str`

Returns the path to the top-level namespace package under `src/`.

| Input | Output |
|---|---|
| `"collective.myaddon"` | `"src/collective"` |
| `"plone.app.content"` | `"src/plone"` |

---

## `package_path`

**Signature**: `package_path(v: str) -> str`

Returns the full package path relative to `src/`, replacing dots with slashes.

| Input | Output |
|---|---|
| `"collective.myaddon"` | `"collective/myaddon"` |
| `"plone.app.content"` | `"plone/app/content"` |
| `"myaddon"` | `"myaddon"` |

---

## `pascal_case`

**Signature**: `pascal_case(package_name: str) -> str`

Converts an underscore-separated name to PascalCase (title-casing each segment).

| Input | Output |
|---|---|
| `"my_plone_addon"` | `"MyPloneAddon"` |
| `"collective"` | `"Collective"` |

---

## `extract_host`

**Signature**: `extract_host(hostname: str) -> str`

Returns the first segment of a dotted hostname.

| Input | Output |
|---|---|
| `"mysite.example.com"` | `"mysite"` |
| `"localhost"` | `"localhost"` |

---

## `use_prerelease_versions`

**Signature**: `use_prerelease_versions(_: str) -> str`

Returns `"Yes"` when the environment variable `USE_PRERELEASE` is set; otherwise `"No"`.
The input value is ignored.

| `USE_PRERELEASE` set | Output |
|---|---|
| Yes | `"Yes"` |
| No | `"No"` |

---

## `latest_volto`

**Signature**: `latest_volto(use_prerelease_versions: str) -> str`

Returns the latest released version of Volto.
Pass `"Yes"` to include pre-releases.

| Input | Output (example) |
|---|---|
| `"No"` | `"18.6.0"` |
| `"Yes"` | `"19.0.0-alpha.1"` |

Requires internet access.

---

## `latest_plone`

**Signature**: `latest_plone(use_prerelease_versions: str) -> str`

Returns the latest released version of Plone.
Pass `"Yes"` to include pre-releases.

| Input | Output (example) |
|---|---|
| `"No"` | `"6.1.2"` |
| `"Yes"` | `"6.2.0a1"` |

Requires internet access.

---

## `python_versions`

**Signature**: `python_versions(plone_version: str) -> list[str]`

Returns the list of Python versions supported by the given Plone version.

| Input | Output (example) |
|---|---|
| `"6.0"` | `["3.10", "3.11", "3.12"]` |
| `"6.1"` | `["3.10", "3.11", "3.12", "3.13"]` |

---

## `python_version_earliest`

**Signature**: `python_version_earliest(plone_version: str) -> str`

Returns the earliest Python version supported by the given Plone version.

| Input | Output |
|---|---|
| `"6.0"` | `"3.10"` |
| `"6.1"` | `"3.10"` |

---

## `python_version_latest`

**Signature**: `python_version_latest(plone_version: str) -> str`

Returns the latest Python version supported by the given Plone version.

| Input | Output |
|---|---|
| `"6.0"` | `"3.12"` |
| `"6.1"` | `"3.13"` |

---

## `node_version_for_volto`

**Signature**: `node_version_for_volto(volto_version: str) -> int`

Returns the recommended Node.js major version for the given Volto version.

| Input | Output (example) |
|---|---|
| `"18.6.0"` | `22` |
| `"19.0.0"` | `24` |

---

## `gs_language_code`

**Signature**: `gs_language_code(code: str) -> str`

Converts a language code to the format expected by Plone's Generic Setup (lowercase base, lowercase country).

| Input | Output |
|---|---|
| `"en"` | `"en"` |
| `"pt-BR"` | `"pt-br"` |
| `"zh-CN"` | `"zh-cn"` |

---

## `locales_language_code`

**Signature**: `locales_language_code(code: str) -> str`

Converts a language code to the format expected by GNU gettext (lowercase base, uppercase country, underscore separator).

| Input | Output |
|---|---|
| `"en"` | `"en"` |
| `"pt-BR"` | `"pt_BR"` |
| `"zh-CN"` | `"zh_CN"` |

---

## `image_prefix`

**Signature**: `image_prefix(registry: str) -> str`

Returns the Docker image prefix for the given registry hostname.

---

## `as_semver`

**Signature**: `as_semver(v: str) -> str`

Converts a PEP 440 version string to SemVer format.

| Input | Output |
|---|---|
| `"6.1.2"` | `"6.1.2"` |
| `"6.0.0a1"` | `"6.0.0-alpha.1"` |

---

## `unscoped_package_name`

**Signature**: `unscoped_package_name(v: str) -> str`

Returns the unscoped name for a scoped npm package.

| Input | Output |
|---|---|
| `"@plone/volto"` | `"volto"` |
| `"mypackage"` | `"mypackage"` |

---

## `as_major_minor`

**Signature**: `as_major_minor(v: str) -> str`

Truncates a version string to `MAJOR.MINOR`.

| Input | Output |
|---|---|
| `"6.1.2"` | `"6.1"` |
| `"3.10.1"` | `"3.10"` |

---

## Related pages

- {doc}`/how-to-guides/use-built-in-filters`: how to use filters in a template.
- {doc}`/how-to-guides/add-a-filter`: add a new built-in filter to Cookieplone.
- {doc}`/concepts/validators-and-filters`: how filters differ from validators.
