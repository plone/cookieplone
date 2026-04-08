# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 2.0.0a1 (2026-04-08)


### New features:

- Get default values for author and email from git config. @ericof [#51](https://github.com/plone/cookieplone/issues/51)
- Support grouped template selection in the CLI when ``cookieplone-config.json`` defines ``groups``. Users first pick a category, then a template within that category. @ericof [#118](https://github.com/plone/cookieplone/issues/118)
- Added `cookieplone.utils.subtemplates.run_subtemplates()`, a helper that post-generation hooks can use to drive sub-template generation via an explicit `{template_id: handler}` dispatch dict, with a default fallback for sub-templates that do not need custom handling. The legacy `cookieplone.generator.generate_subtemplate()` entry point is now deprecated. @ericof [#119](https://github.com/plone/cookieplone/issues/119)
- Dump user answers to a .cookieplone.json file. inside the newly created codebase. @ericof [#121](https://github.com/plone/cookieplone/issues/121)
- Support global version pinning from repository-level ``cookieplone-config.json``. Templates access shared versions via ``{{ versions.<key> }}`` with per-template overrides taking precedence. @ericof [#128](https://github.com/plone/cookieplone/issues/128)
- Added support for tui-forms to ask user for answers. @ericof [#134](https://github.com/plone/cookieplone/issues/134)
- Handle pre-prompt-hook fails without raising Typer errors. @ericof [#137](https://github.com/plone/cookieplone/issues/137)
- Implemented `cookieplone-config.json` repository configuration format with JSON Schema validation, grouped templates, global version pinning, and backward-compatible fallback to `cookiecutter.json`. @ericof [#141](https://github.com/plone/cookieplone/issues/141)
- Updated tui-forms to 1.0.0a2 with confirmation page, back-navigation, specific validation error messages, and JSONSchema constraint keywords support. @ericof [#142](https://github.com/plone/cookieplone/issues/142)
- Refactored v2 config format to separate schema from generator configuration, with `SubTemplate` TypedDict, `config.versions` as a top-level context namespace, and Jinja2 rendering for subtemplate `enabled` fields. @ericof [#156](https://github.com/plone/cookieplone/issues/156)
- Added support for selecting the `tui_forms` renderer used by the wizard. The renderer can be set via the `config.renderer` field in `cookieplone-config.json` or via the `COOKIEPLONE_RENDERER` environment variable, which takes precedence. The `--no-input` flag still forces the `noinput` renderer. Invalid renderer names are reported with a clear error listing the available options. @ericof [#165](https://github.com/plone/cookieplone/issues/165)
- Implement cutter2plone command line utility to convert cookiecutter.json files to cookieplone.json. @ericof 
- Implement generator logic to work with the new form wizard. @ericof 
- Implement validators for plone_version, volto_version, python_package_name, hostname, language_code. @ericof 
- Support loading answers from a json file by passing --answers or --answers-file. @ericof 
- Tag option of the cli can be passed with `--branch` or `--tag`. @ericof 


### Bug fixes:

- Fixed `create_namespace_packages` to handle re-runs gracefully — existing namespace directories and destination packages are no longer raised as errors when running with the `-f` flag. @ericof [#139](https://github.com/plone/cookieplone/issues/139)
- Fixed ``OutputDirExistsException`` not properly handled — added a dedicated ``OutputDirExistsException`` subclass with a user-friendly error message, fixed ``CookieploneException`` hierarchy to call ``super().__init__()``, and added a ``parse_output_dir_exception`` helper to extract the directory path from cookiecutter errors. @ericof [#140](https://github.com/plone/cookieplone/issues/140)
- v1→v2 config converter now produces JSONSchema-compliant ``oneOf`` with ``const``/``title`` instead of the non-standard ``options`` keyword for choice fields. @ericof [#143](https://github.com/plone/cookieplone/issues/143)
- Fixed ``RepositoryException`` losing its error message and removed dead exception handlers in the generator module. @ericof [#147](https://github.com/plone/cookieplone/issues/147)
- Fixed `Cookies.bake()` helper to load `global_versions` from `cookieplone-config.json` so templates tested via pytest can resolve `{{ versions.<key> }}` the same way the CLI does. @ericof [#164](https://github.com/plone/cookieplone/issues/164)
- Fixed `write_answers()` so that the `__template__` key is actually persisted to the generated `.cookieplone_answers_*.json` file. The key is now written to the persisted copy in both interactive and `--no-input` modes, and `write_answers()` no longer mutates the live wizard state. @ericof [#168](https://github.com/plone/cookieplone/issues/168)
- Fixed `latest_volto` and `latest_plone` filters so they accept either a string or a boolean value, allowing them to be used in v2 schemas where `use_prerelease_versions` is declared as a `boolean` property. `parse_boolean` now handles `str`, `bool`, and `int` inputs. @ericof [#169](https://github.com/plone/cookieplone/issues/169)
- Use the `--all` option to list all templates, including hidden ones. @ericof 


### Internal:

- Implement get_user_config to load user configuration from files. @ericof [#51](https://github.com/plone/cookieplone/issues/51)
- Added VSCode recommended extensions and settings. @ericof [#123](https://github.com/plone/cookieplone/issues/123)
- Added GHA to deploy documentation to GitHub pages. @ericof [#132](https://github.com/plone/cookieplone/issues/132)
- Refactored `generate()` API: consolidated 15 positional parameters into a `GenerateConfig` dataclass. @ericof [#146](https://github.com/plone/cookieplone/issues/146)
- Code health: moved ``parse_boolean`` to ``utils.parsers``, fixed ``import_patch`` exception safety, added ``quiet_mode()`` context manager, and resolved stale TODO comments. @ericof [#148](https://github.com/plone/cookieplone/issues/148)
- Replaced formatter library imports (``black``, ``isort``, ``zpretty``, ``ruff``) with ``uvx`` subprocess calls, removing them from runtime dependencies. @ericof [#154](https://github.com/plone/cookieplone/issues/154)
- Aligned ruff isort configuration with the rest of the Plone ecosystem: single-line, no-sections, `from`-first imports with two blank lines after the import block. Reformatted the entire codebase in one sweep. @ericof [#171](https://github.com/plone/cookieplone/issues/171)
- Add a CODEOWNERS configuration to the repository. @ericof 
- Added a `.git-blame-ignore-revs` file so the codebase-wide isort reformat (#171) can be skipped when running `git blame`. @ericof 
- Update `make coverage` command to use `coverage run -m pytest` instead of `pytest --cov` . @ericof 


### Documentation:

- Documented how to drive sub-template generation from a post-generation hook with `run_subtemplates()` and a dictionary of custom handlers, using the `monorepo` project template as a reference. @ericof [#119](https://github.com/plone/cookieplone/issues/119)
- Added comprehensive documentation about cookieplone and how to create new templates. @ericof [#132](https://github.com/plone/cookieplone/issues/132)
- Documented how to run a prerelease version of Cookieplone with `uvx` in both the README and the how-to guides, covering exact version pinning, `--prerelease=allow`, and persistent `uv tool install` workflows. @ericof 


### Tests

- Added tests for config loaders (v1, v2), settings, wizard, and generator modules. @ericof [#145](https://github.com/plone/cookieplone/issues/145)
- Reimplement the fixtures from pytest-cookies to use the new cookieplone and schemas. @ericof 

## 1.0.0 (2026-03-13)


### New features:

- Add support to Python 3.14. @ericof 


### Bug fixes:

- Remove dependency on `chardet`. Now we have a version of `binaryornot` that does not depend on `chardet`. @wesleybl [#125](https://github.com/plone/cookieplone/issues/125)


### Internal:

- Update dependencies semver==3.0.4, typer==0.24.1, packaging==26.0, gitpython==3.1.46, xmltodict==1.0.4, black==26.3.1 @ericof [#130](https://github.com/plone/cookieplone/issues/130)
- Add dependabot support for GitHub Actions. @ericof 
- Fix pyproject.toml metadata. @ericof 
- Update pre-commit hooks (uv run pre-commit autoupdate). @ericof 


### Tests

- Update GitHub actions' versions. @ericof 

## 0.9.11 (2026-03-04)


### New features:

- Default to create Python native namespaces @gforcada [#115](https://github.com/plone/cookieplone/issues/115)


### Bug fixes:

- Fix dependency pinning: Require chardet<7 to work around an incompatibility with binaryornot. @davisagli 

## 0.9.10 (2025-10-21)


### Bug fixes:

- Add support for NodeJS 24. @davisagli 

## 0.9.9 (2025-10-04)


### New features:

- Use a compacter logo. @ericof, @acsr [#112](https://github.com/plone/cookieplone/issues/112)


### Bug fixes:

- Add error handling for connectivity issues in filters `latest_volto` and `latest_plone`. @ericof [#110](https://github.com/plone/cookieplone/issues/110)

## 0.9.8 (2025-09-19)


### Bug fixes:

- Fix ruff format call. @gil-cano [#104](https://github.com/plone/cookieplone/issues/104)
- Fixed boolean cli options converted to strings. Upgrade `typer` dependency. @sneridagh [#109](https://github.com/plone/cookieplone/issues/109)
- Fix missing newline in output. @davisagli 


### Documentation:

- Replace pipx with uvx in README. @gil-cano [#102](https://github.com/plone/cookieplone/issues/102)

## 0.9.7 (2025-04-17)


### New features:

- Update variable_pattern fixture to support also usage in hook files. @stevepiercy [#100](https://github.com/plone/cookieplone/issues/100)


### Internal:

- Correct spelling of "subtemplate" and "add-on" in text, not code. @stevepiercy [#95](https://github.com/plone/cookieplone/issues/95)


### Documentation:

- Fix uv brand name. @stevepiercy [#96](https://github.com/plone/cookieplone/issues/96)

## 0.9.6 (2025-03-31)


### New features:

- Support `hidden` option for templates listed in `cookiecutter.json`. @ericof [#93](https://github.com/plone/cookieplone/issues/93)

## 0.9.5 (2025-03-27)


### Bug fixes:

- Honor COOKIEPLONE_REPOSITORY_TAG environment variable on cookieplone initialization. @ericof [#89](https://github.com/plone/cookieplone/issues/89)
- Display a friendly message if a template is not registered with cookiecutter.json @ericof [#90](https://github.com/plone/cookieplone/issues/90)

## 0.9.4 (2025-03-27)


### New features:

- Refactor template list handling to use the template path information available at cookiecutter.json @ericof [#87](https://github.com/plone/cookieplone/issues/87)


### Internal:

- Fix `make release` to also create the tag during the release process @ericof 

## 0.9.3 (2025-03-25)


### New features:

- Add `as_major_minor` filter. @ericof 
- Add `package_namespace_path` filter. @ericof 
- Refactor extra-context parsing. @ericof 


### Documentation:

- Update README to recommend using `cookieplone` via `uvx` @ericof 


### Tests

- Add session fixture `annotate_context`. @ericof 

## 0.9.2 (2025-03-25)


### Bug fixes:

- Fix regression in generating namespace packages. @davisagli [#80](https://github.com/plone/cookieplone/issues/80)

## 0.9.1 (2025-03-24)


### Bug fixes:

- Fix namespace generation issue @ericof 


### Internal:

- Ignore CHANGES.md from the `trailing-whitespace` pre-commit check. @ericof 

## 0.9.0 (2025-03-24)


### New features:

- Implement new filters to manipulate Python versions. @ericof [#69](https://github.com/plone/cookieplone/issues/69)
- Format Python codebase with ruff, if pyproject.toml has the configuration. @ericof [#71](https://github.com/plone/cookieplone/issues/71)
- Add filter `as_semver` to convert Python versions (PEP 440) to SemVer. @ericof [#73](https://github.com/plone/cookieplone/issues/73)
- Add filter `unscoped_package_name` to return the npm package name without its scope. @ericof [#74](https://github.com/plone/cookieplone/issues/74)
- Add `__generator_sha` to the variables to report the last commit on the templates repo @ericof 
- Create namespace packages using `pkgutil` instead of `pkg_resources` as new packages are not setuptools based @ericof 


### Internal:

- Use uv to manage the environment. @ericof [#76](https://github.com/plone/cookieplone/issues/76)

## 0.8.4 (2025-02-22)


### Bug fixes:

- Added an exception for sanity check command failure due to permission error. @ewohnlich [#62](https://github.com/plone/cookieplone/issues/62)
- Fix outdated references to cookiecutter-plone. @davisagli [#65](https://github.com/plone/cookieplone/issues/65)

## 0.8.3 (2025-02-04)


### Bug fixes:

- Fix parsing of boolean values for use_prerelease_versions. @davisagli [#47](https://github.com/plone/cookieplone/issues/47)
- Use the `init.defaultBranch` setting in git `config` if available, else `main`, as the branch name for new git repositories. @davisagli
  customized via the `init.defaultBranch` setting in git config. @davisagli [#135](https://github.com/plone/cookieplone/issues/135)

## 0.8.2 (2025-01-14)


### Bug fixes:

- Add support for Python 3.13. @davisagli [#54](https://github.com/plone/cookieplone/issues/54)

## 0.8.1 (2024-11-13)


### Bug fixes:

- Fix validation of Volto and Node versions. @davisagli [#49](https://github.com/plone/cookieplone/issues/49)

## 0.8.0 (2024-11-07)


### New features:

- Support Python package names with no namespace or multiple namespaces. @davisagli [#43](https://github.com/plone/cookieplone/issues/43)


### Bug fixes:

- Show a more helpful error message if user enters a Python package name without a namespace. @davisagli [#36](https://github.com/plone/cookieplone/issues/36)
- Fix error with `--replay`. @davisagli [#37](https://github.com/plone/cookieplone/issues/37)
- Rename the `--no_input` option to `--no-input` for consistency with other options. @davisagli [#41](https://github.com/plone/cookieplone/issues/41)


### Documentation:

- Fix environment variable name
  [erral] [#42](https://github.com/plone/cookieplone/issues/42)

## 0.7.1 (2024-05-29)


### Bug fixes:

- Fix issue with Welcome Screen display [@ericof]

## 0.7.0 (2024-05-27)


### New features:

- Add --info option to display current settings [@ericof] [#27](https://github.com/plone/cookieplone/issues/27)
- Add pytest fixtures to be used in template development [@ericof] [#29](https://github.com/plone/cookieplone/issues/29)

## 0.6.3 (2024-05-17)


### Bug fixes:

- Fix usage of formatter functions in a pipx environment [@ericof]

## 0.6.2 (2024-05-17)


### New features:

- Add helper function to format a Python codebase [@ericof]


### Internal:

- Configure logger for cookieplone [@ericof]

## 0.6.1 (2024-05-17)


### Bug fixes:

- Small fixes to cookieplone/utils/plone.py functions [@ericof]

## 0.6.0 (2024-05-17)


### New features:

- Add functions `add_dependency_profile_to_metadata` and `add_dependency_to_zcml` to manipulate Plone files [@ericof] [#25](https://github.com/plone/cookieplone/issues/25)

## 0.5.7 (2024-05-16)


### Bug fixes:

- Fix usage of `--replay-file` [@ericof] [#23](https://github.com/plone/cookieplone/issues/23)

## 0.5.6 (2024-05-16)


### Bug fixes:

- Handle in `cookieplone.generator._get_repository_root` the local development of templates containing pre_prompt hooks [@ericof]

## 0.5.5 (2024-05-16)


### Bug fixes:

- Fix `cookieplone --version` cli command [@ericof]

## 0.5.4 (2024-05-16)


### Bug fixes:

- Fix `cookieplone.generator._get_repository_root` to get the repository from the **_repo_dir** context variable [@ericof] [#20](https://github.com/plone/cookieplone/issues/20)

## 0.5.3 (2024-05-15)


### Bug fixes:

- Fix extra_context parsing [@ericof] [#18](https://github.com/plone/cookieplone/issues/18)

## 0.5.2 (2024-05-13)


### Bug fixes:

- Set default `tag` value to **main** instead of the empty string [@ericof] [#15](https://github.com/plone/cookieplone/issues/15)

## 0.5.1 (2024-05-07)


### Internal:

- Use `gh:plone/cookieplone-templates` as the default repository [@ericof] [#13](https://github.com/plone/cookieplone/issues/13)

## 0.5.0 (2024-04-27)


### Internal:

- Move from poetry to hatch to manage the environment [@ericof] [#9](https://github.com/plone/cookieplone/issues/9)


### Documentation:

- Initial documentation (README.md) for cookieplone [@ericof] [#8](https://github.com/plone/cookieplone/issues/8)
