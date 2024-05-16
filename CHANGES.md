# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

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
