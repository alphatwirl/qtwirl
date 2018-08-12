# Changelog

## [Unreleased]

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.04.0...master))
- renamed the 1st argument of `qtwirl()` `file` `data`
- updated `reader_cfg`
    - now `reader` can be a list of readers
    - changes in `table_cfg`
        - renamed keys
              - `keyAttrNames` -> `key_name`
              - `keyIndices` -> `key_index`
              - `binnings` -> `key_binning`
              - `keyOutColumnNames` -> `key_out_name`
              - `valAttrNames` -> `val_name`
              - `valIndices` -> `val_index`
              - `summaryClass` -> `agg_class`
              - `summaryColumnNames` -> `agg_name`
        - added new keys: `store_file`, `file_path`, `file_name`,
          `file_dir`
    - changes in `selection_cfg`
        - now the full form is `dict(condition=condition)`
        - added new keys: `store_file`, `file_path`, `file_name`,
          `file_dir`, `count`
- added option to make cutflow table
- added option to store results to files
- reorganized directory structure, created new private sub-packages
  `_parser` and `_builder`
- added ``pytest.ini`` file

## [0.04.0] - 2018-08-09

**PyPI**: https://pypi.org/project/qtwirl/0.4.0/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.03.4...v0.04.0))
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
