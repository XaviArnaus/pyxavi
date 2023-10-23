# Changelog

## [v0.5.4](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.5.4) - 2023-10-23

### Added

- The ability for `Config` to merge dicts into the current instance. This enables to enrich the configs on the fly

## [v0.5.3](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.5.3) - 2023-10-18

### Added

- The ability for `Config` to merge config files into the current instance. This enables to use several config files under a single Config instance.

## [v0.5.2](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.5.2) - 2023-10-13

### Added

- The ability for `Logger` to receive a `base_path` so that the path can be correctly set, beyond what is said in the config.

## [v0.5.1](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.5.1) - 2023-10-06

### Changed

- Corrected links in version titles in the Changelog

## [v0.5.0](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.5.0) - 2023-10-06

### Added

- New `Network` class to gather and validate some data

### Changed

- Changelog iterated to adhere to [Common Changelog](https://common-changelog.org). Will start from this version on.

### Removed

- **Breaking:** Removed `logger.getLogger()` as defined in previous version

## [v0.4.1](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.4.1)

- Added missing documentation

## [v0.4.0](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.4.0)

- Add `firefish` class as a wrapper for the Firefish API calls that I need
- Add a `logger.get_logger()` and mark `logger.getLogger()` as deprecated, to be removed in v0.5.0

## [v0.3.3](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.3.3)

- Bump PyYaml to version 6.0.1 as 6.0 is broken

## [v0.3.2](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.3.2)

- Make non built-in objects inspection depth controlable in `dd` recurdive call

## [v0.3.1](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.3.1)

- Iterate over the `pyproject.toml` and the `README.md` to make them more appealing in pypi.org

## [v0.3.0](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.3.0)

- Rewrite the `debugger.dd`.
- New `terminal_color` class for printing with colors.

## [v0.2.1](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.2.1)

- Add traceback function to debugger lib.

## [v0.2.0](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.2.0)

- Add *Janitor* API wrapper

## [v0.1.5](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.1.5)

- Bugfix in Storage when set needs to identify empty dictionaries

## [v0.1.4](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.1.4)

- Initialize in-memory stack for Storage when the file is just touched

## [v0.1.3](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.1.3)

- Make Logger to create the log file in case it does not exist yet

## [v0.1.2](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.1.2)

- Bump Poetry required version to 1.2.0

## [v0.1.1](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.1.1)

- Minor fix in `Media`.

## [v0.1.0](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.1.0)

- Move from `setup.py` to `pyproject.toml`
- Apply Flake8 & Yapf
- Add some basic tests
- Some fixes thanks to tests
- Rename the project from `python-bundle` to `pyxavi`
- Add some Docstrings
- Merge together `Media` and `Downloader` into `Media`
- `Media` methods renamed

## [v0.0.6](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.0.6)

- Added `Downloader`

## [v0.0.5](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.0.5)

- Added `Media`

# [v0.0.4](https://github.com/XaviArnaus/pyxavi/releases/tag/v0.0.4)

- Created package
- Added `Config`, `Logger`, `Storage` and `Debugger`