# Changelog

## [Unreleased]

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.9.2...master))

## [0.9.2] - 2019-06-07

**PyPI**: https://pypi.org/project/qtwirl/0.9.2/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.9.1...v0.9.2))
- fixed a bug where successive calls of `_expand_config()` shared `shared`
- started applying default to `table_cfg` and `selection_cfg`
- cleaned code
- updated tests

## [0.9.1] - 2019-05-11

**PyPI**: https://pypi.org/project/qtwirl/0.9.1/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.9.0...v0.9.1))
- updated `.travis.yml`, `setup.py`
- updated README.md

## [0.9.0] - 2019-03-10

**PyPI**: https://pypi.org/project/qtwirl/0.9.0/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.07.0...v0.9.0))
- updated `.travis.yml`, `MANIFEST.in`, `setup.py`

## [0.07.0] - 2019-02-10

**PyPI**: https://pypi.org/project/qtwirl/0.7.0/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.06.0...v0.07.0))
- changed the default `quiet` to `False`

## [0.06.0] - 2018-08-15

**PyPI**: https://pypi.org/project/qtwirl/0.6.0/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.05.0...v0.06.0))
- defined `expander.py` as a generic module, which can become an independent package in the future.
- improved internal structure

## [0.05.0] - 2018-08-12

**PyPI**: https://pypi.org/project/qtwirl/0.5.0/

#### Changs from the previous release: ([diff](https://github.com/alphatwirl/qtwirl/compare/v0.04.0...v0.05.0))
- changed the minimum required versoin of AlphaTwirl to 0.20.0
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
