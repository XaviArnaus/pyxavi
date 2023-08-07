# v0.3.2

- Make non built-in objects inspection depth controlable in `dd` recurdive call

# v0.3.1

- Iterate over the `pyproject.toml` and the `README.md` to make them more appealing in pypi.org

# v0.3.0

- Rewrite the `debugger.dd`.
- New `terminal_color` class for printing with colors.

# v0.2.1

- Add traceback function to debugger lib.

# v0.2.0

- Add *Janitor* API wrapper

# v0.1.5

- Bugfix in Storage when set needs to identify empty dictionaries

# v0.1.4

- Initialize in-memory stack for Storage when the file is just touched

# v0.1.3

- Make Logger to create the log file in case it does not exist yet

# v0.1.2

- Bump Poetry required version to 1.2.0

# v0.1.1

- Minor fix in `Media`.

# v0.1.0

- Move from `setup.py` to `pyproject.toml`
- Apply Flake8 & Yapf
- Add some basic tests
- Some fixes thanks to tests
- Rename the project from `python-bundle` to `pyxavi`
- Add some Docstrings
- Merge together `Media` and `Downloader` into `Media`
- `Media` methods renamed

# v0.0.6

- Added `Downloader`

# v0.0.5

- Added `Media`

# v0.0.4

- Created package
- Added `Config`, `Logger`, `Storage` and `Debugger`