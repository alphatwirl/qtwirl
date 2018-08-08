# Changelog

## [Unreleased]

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.03.4...master))
- changed options to `qtwirl()`
    - no longer necessary to give `"qtwirl"` to `user_modules`
    - default of `dispatcher_options` is now `None` not an empty dict
      (was mutable default)
    - default of `user_modules` is now `None` not an empty tuple
- refactored code in main.py
- added a check for empty input (e.g., all files are zombie)
    - return a list of empty data frames (was raising exception)
- updated README.md
- added CHANGELOG.md

## [0.03.4] - 2018-08-02

**PyPI**: https://pypi.org/project/qtwirl/0.3.4/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.03.3...v0.03.4))
- added new option `skip_error_files` to `qtwirl()
- changed the minimum required versoin of AlphaTwirl to 0.18.5
