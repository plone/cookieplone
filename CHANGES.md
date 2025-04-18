# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

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
