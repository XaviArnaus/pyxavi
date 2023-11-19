# `Logger` module

## Default values for not coming parameters:

When the received `Config` instance does not contain any of the expected parameters, the following default parameters will be used to fill the blanks:

```Python
{
    "name": "custom_logger",
    "loglevel": 20,
    "format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
    "file": {
        "active": False,
        "filename": "debug.log",
        "encoding": "UTF-8",
        "rotate": {
            "active": False,
            "when": "midnight",
            "backup_count": 10,
            "utc": False,
            "at_time": "1:0:0"
        },
    },
    "stdout": {
        "active": False
    }
}
```

## Old versus new `logger` *Config* parameter set

The first iteration of the `Logger` module, that stood active until the `pyxavi` *v0.7.7*, **EXPECTS** to receive a `Config` instance that loaded its parameter set from a structure like the following:

```yaml
# Logging config
logger:
  # [Integer] Log level: NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50
  loglevel: 10
  # [String] Name of the logger
  name: "my_app"
  # [Bool] Dump the log into a file
  to_file: True
  # [String] Path and filename of the log file
  filename: "log/my_app.log"
  # [Bool] Dump the log into a stdout
  to_stdout: True
  # [String] Format of the log
  format: "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
```

- The parameter set was mandatory
- The object structure was flat
- There is no support for log rotation

From the version *v0.8.0 on, the `Config` instance **MAY** be loaded by a parameter set which has now a different structure:

```yaml
# Logging config
logger:
  # [Integer] Log level: NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50
  loglevel: 10
  # [String] Name of the logger
  name: "my_app"
  # [String] Format of the log
  format: "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
  # File related parameters
  file:
    # [Bool] Dump the log into a file
    active: False
    # [String] Path and filename of the log file
    filename: "log/my_app.log"
    # [String] The encoding of the log file
    encoding: "UTF-8"
    # [Bool] Do we want to rotate the log files? Only will apply if we log to files
    rotate:
        active: False
        # [String] When do we rotate. Accepts "S" | "M" | "H" | "D" | "W0"-"W6" | "midnight"
        #   See https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
        when: "midnight"
        # [Int] How many rotated old files to keep before it starts to delete the older
        backup_count: 10
        # [Bool] Stick to UTC timings when triggering the rotation
        utc: False
        # [String] in format "%H:%M:%S". When to trigger THE VERY FIRST rotation.
        #   Subsequent will attend to when_rotate
        at_time: "1:00:00"
  # Standard output related parameters
  stdout:
  # [Bool] Dump the log into a stdout
      active: True
```

- The parameter set is optional. All or part of the parameters may not be delivered and these will be filled with default values.
- The object structure is nested
- There is support for log rotation with `TimedRotatingFileHandler` parameters

In the *v0.8.0* version, passing a `Config` instance that loaded its parameter set from the old structure will register a WARNING log message with the following note:

```
[pyxavi] An old version of the configuration file structure for the Logger module has been loaded. This is deprecated.
Please migrate your configuration file to the new structure.
Read https://github.com/XaviArnaus/pyxavi/blob/main/docs/logger.md
```


