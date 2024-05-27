# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

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
