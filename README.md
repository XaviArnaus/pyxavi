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


## The `Queue` module

A class to manage fifo queue style lists relying in the `Storage` module.


## The `Config` module

A class for read-only config values inheriting from the `Storage` module.


## The `Logger` module

A class that helps setting up a built-in logger based on the configuration in a file, handled
by the `Config` module.

For example, a `config.yaml` with all parameters to configure the logger explicitly defined would look like this:
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

Read more about the [`Logger` module](docs/logger.md).

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

At this point of time it only covers:
- Posting a new status (creating a note in Firefish).
- Posting new media (create a drive/media in Firefish)

## The `Network` module

A class to perform some networking actions. At this point:
- Get the external IP addres for IPv4 and IPv6
- Validate an IPv4 and IPv6 IP address

## The `Url` module

A class to perform some actions over URLs. At this point:
- Clean the URL based on given parameters
- Validate URLs
- Discover the Feed URL from a given site URL

## The `MastodonHelper` module

A class that abstracts the instantiation of the Mastodon-like API wrapper. At this point it
supports the original *Mastodon.py* wrapper that at its time supports Mastodon, Pleroma and Akkoma,
and Firefish through the `Firefish` module above (which support is limited).

The class is meant to receive an object `MastodonConnectionParams` that is responsible of bringing in
the parameters that facilitate the connection to the Mastodon wrappers and define some specifics
regarding the server connecting to, like maximum *post length and visibility*.

Also includes a `StatusPost` that is meant to encapsulate everything that is needed to represent
a Status to be posted. Internally it makes use of `StatusPostVisibility` and `StatusPostContentType`
that are also referenced from the `MastodonConnectionParams`. While this object is meant to easy the
transport of the status publishing item, it is not required and totally optional.

The benefit of using this set of tools is to encapsulate and abstract what is needed to initiate
a connection to the Mastodon-like API and post a status, including the authorisation, making it 
really simple to include into a given app. One can even instantiate different wrappers to publish
into different servers at the same time.

```python
connection_params = MastodonConnectionParams.from_dict({
  "app_name": "SuperApp",
  "instance_type": "mastodon",
  "api_base_url": "https://mastodon.social",
  "credentials": {
    "user_file": "user.secret",
    "client_file": "client.secret",
    "user": {
        "email": "bot@my-fancy.site",
        "password": "SuperSecureP4ss",
    }
  }
})

mastodon_instance =  MastodonHelper.get_instance(
  connection_params=connection_params
)

mastodon_instance.status_post(
  status="I am a text"
)
```

## The `MastodonPublisher` module

A class that abstracts the process of publishing text and media into a Mastodon-like API.

Benefits of using it:
- Total encapsulation of `MastodonHelper` related work.
- Facilitates methods to publish simple text, full `StatusPost` objects and media URLs or paths.
- Retries with delay in case the communication is poor.
- Slices the text so that it fits within the defined status maximum length
- Proxies the posting through any of the supported instance types.
- Supports the definition of a *dry run* so that execution can be tested without actual publishing
- Supports parametrisation through `Config` objects

Having a `Config` like the following YAML:
```yaml
publisher:
  media_storage: "storage/media/"
  dry_run: False
  named_account: test
mastodon:
  named_accounts:
    test:
      app_name: "Test"
      api_base_url: "https://mastodon.social"
      instance_type: "mastodon"
      credentials:
        client_file: "client_test.secret"
        user_file: "user_test.secret"
        user:
          email: "test@my-fancy.site"
          password: "SuperSecureP4ss"
```

Publishing is as simple as:
```Python
Publisher(config=Config()).publish_text("This is a test")
```


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
    file:
      active: True
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
$ python test.py
(Config){
  "_filename": (str[11])"config.yaml",
  "_content": (dict[2]){
    "app": (dict[1]){"name": (str[6])"My app"},
    "logger": (dict[2]){
      "name": (str[6])"my_app",
      "file": (dict[1]){"active": (bool)True}
    }
  },
  "_separator": (str[1])".",
  class methods: _Dictionary__recursive_set, _get_horizontally, _get_parent_horizontally, _is_int, _is_out_of_range, _load_file_contents, _merge_complex_recursive, _merge_simple_recursive, _remove_none_recursive, _set_horizontally, delete, get, get_all, get_hashed, get_keys_in, get_last_key, get_parent, get_parent_path, initialise_recursive, key_exists, merge, merge_from_dict, merge_from_file, needs_resolving, read_file, remove_none, reso
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
- [x] Empty the [NEXT MAJOR](./NEXT_MAJOR.md) list
