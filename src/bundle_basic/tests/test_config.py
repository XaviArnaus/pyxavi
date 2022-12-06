from unittest.mock import patch, mock_open
from bundle_basic.config import Config

CONFIG = {"foo": {"bar": "hola", "foo2": {"bar2": "adios"}}, "que": "tal"}


def patched_yaml_safe_load(stream):
    return CONFIG


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
def test_initialize_config():
    config = Config()

    assert config._config == CONFIG


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
def test_get_all():
    config = Config()

    assert config.get_all() == CONFIG


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
def test_get_first_level():
    config = Config()

    assert config.get("que") == CONFIG["que"]


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
def test_get_second_level():
    config = Config()

    assert config.get("foo.bar") == CONFIG["foo"]["bar"]


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
def test_get_third_level():
    config = Config()

    assert config.get("foo.foo2.bar2") == CONFIG["foo"]["foo2"]["bar2"]
