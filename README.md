# The Xavi's Python package

Set of utilities to assist on simple Python projects.

## Disclaimer

This is a constant *work in progress* package, adding and improving the libraries within with
the goal of abstracting and reusing code, and easing the coding experience of real life
projects.

Suggestions are welcome :)


# Modules included in the package

This package contains a set of modules, divided by functionality.


## The `Dictionary` module

A class to bring some extras to work with `dict` object files, like getter and setter, checks,
and a way to trasverse the object with keys like `family.category.parameter1.subparameter2`

For example, consider the following snippet:

```python
from pyxavi.dictionary import Dictionary

d = {
  "a": 1,
  "b": "B",
  "c": [1, 2],
  "d": {"d1": "D1", "d2": "D2"},
  "e": [
    {"e1": "E1"},
    {"e2": {"e21": "E21"}}
  ]
}

instance = Dictionary(d)

assert instance.get("a") == 1
assert instance.get("c.0") == 1
assert instance.get("d.d1") == "D1"
assert instance.get("e.1.e2.e21") == "E21"
assert instance.get("d.d3", "default") == "default"

assert instance.key_exists("f.f1.foo") is False
instance.initialise_recursive("f.f1.foo")
assert instance.key_exists("f.f1.foo") is True
instance.set("f.f1.foo", "bar")
assert instance.get_parent("f.f1.foo") == {"foo": "bar"}

assert instance.get_keys_in("d") == ["d1", "d2"]
assert instance.delete("d.d9") is False
assert instance.delete("c.1") is True
assert instance.get("c") == [1]

```


## The `Storage` module

A class to bring a basic load/write, get/set behaviour for key/value file based storage. Under
the hood it uses YAML files so they're human readable and inherits from the `Dictionary` module
to apply the easy data manipulation into the loaded yaml files.


## The `Config` module

A class for read-only config values inheriting from the `Storage` module.


## The `Logger` module

A class that helps setting up a built-in logger based on the configuration in a file, handled
by the `Config` module.

For example, a `config.yaml` with parameters to configure the logger would look like this:
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


## The `Debugger` module

A function library with a *PHP's var_dump()*-like function and other debugging tools


## The `TerminalColor` module

A class with a basic set of terminal color codes, ready to assist on printing colorful
terminal messages.


## The `Media` module

A class for operations with media files, at this point extracting media URLs from texts and
download files discovering the mime types.


## The `Janitor` module

A class that wraps the API to report to [Janitor](https://github.com/XaviArnaus/janitor), a
separated GitHub repository project.

## The `Firefish` module

A class that wraps the API for [Firefish](https://firefish.social/api-doc). It is meant to be 
interchangeable with the [Mastodon.py](https://mastodonpy.readthedocs.io/en/latest/index.html) 
wrapper library, so one could inject any of both.

At this point of time it only covers posting a new status (creating a note in Firefish).

## The `Network` module

A class to perform some networking actions. At this point:
- Get the external IP addres for IPv4 and IPv6
- Validate an IPv4 and IPv6 IP address

## The `Url` module

A class to perform some actions over URLs. At this point:
- Clean the URL based on given parameters


# How to use it

1. Assuming you have `pip` installed:
```
pip install pyxavi
```

You can also add the `pyxavi` package as a dependency of your project in its `requirements.txt`
or `pyproject.toml` file.

2. Import the desired module in your code. For example, in your `my_python_script.py`:
```python
from pyxavi.debugger import dd

foo = [1, 2, 3]
dd(foo)
```


# Give me an example

0. First of all you have installed the package, right?
```bash
pip install pyxavi
```

1. Create a yaml file with some params, for example the app's name and the logger. Let's call
it `config.yaml`:
```yaml
app:
    name: My app

logger:
    name: "my_app"
    to_file: True
```

2. Create a python file called `test.py` and open it in your editor.

2. Import the modules by adding these lines in the top of the script file:
```python
from pyxavi.config import Config
from pyxavi.logger import Logger
```

3. Now just add the following lines to instantiate the config and the logger using the config.
```python
config = Config()
logger = Logger(config).get_logger()
```
This will give you a `config` object with the parameters in the config file, and a `logger`
object ready to log events using the built-in interface.

4. Simply use the objects!
```python
app_name = config.get("app.name", "Default app's name")
logger.info(f"The config file says the app's name is {app_name}")
```

Let's see it all together, and extend it a bit more:

```python
from pyxavi.config import Config
from pyxavi.logger import Logger
from pyxavi.debugger import dd

config = Config()
logger = Logger(config).get_logger()

app_name = config.get("app.name", "Default app's name")
logger.info(f"The config file says the app's name is {app_name}")

logger.debug("Inspecting the config object")
dd(config)
```

Now, when it runs it should give the following output:
```bash
$ python3 test.py 
(Config){
  "_filename": (str[11])"config.yaml",
  "_content": (dict[2]){
    "app": (dict[1]){"name": (str[6])"My app"},
    "logger": (dict[2]){"name": (str[6])"my_app", "to_file": (bool)True}
  },
  class methods: _load_file_contents, get, get_all, get_hashed, read_file, set, set_hashed, write_file
}
```

... and also create a `debug.log` file that contains the following content:
```
[2023-08-06 22:24:34,491] INFO     my_app       The config file says the app's name is My app
```

Note that the default `LOG_LEVEL` is 20, therefor the call `logger.debug` was not registered as
it's level is 10.


# ToDo
- [ ] Documentation per module
- [ ] Iterate inline documentation
- [ ] Empty the [NEXT MAJOR](./NEXT_MAJOR.md) list
