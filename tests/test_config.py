from unittest.mock import patch, mock_open
from pyxavi.config import Config
from unittest import TestCase

CONFIG = {"foo": {"bar": "hola", "foo2": {"bar2": "adios"}}, "que": "tal"}


def patched_yaml_safe_load(stream):
    return CONFIG


def os_path_exists_true(path):
    return True


def os_path_exists_false(path):
    return False


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_true)
def initialize():
    return Config()


def test_initialize_config():
    config = initialize()

    assert config._content == CONFIG


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_true)
def test_initialize_config_with_another_filename():
    filename = "another_file.yaml"
    config = Config(filename)

    assert config._filename == filename
    assert config._content == CONFIG


@patch("os.path.exists", new=os_path_exists_false)
def test_initialize_config_file_not_found_exception():
    with TestCase.assertRaises("bundle_basic.config", RuntimeError):
        _ = Config()


def test_get_all():
    config = initialize()

    assert config.get_all() == CONFIG


def test_get_first_level():
    config = initialize()

    assert config.get("que") == CONFIG["que"]


def test_get_second_level():
    config = initialize()

    assert config.get("foo.bar") == CONFIG["foo"]["bar"]


def test_get_third_level():
    config = initialize()

    assert config.get("foo.foo2.bar2") == CONFIG["foo"]["foo2"]["bar2"]


def test_witting_or_setting_is_not_allowed():
    config = initialize()

    with TestCase.assertRaises(config, RuntimeError):
        config.set("foo.foo3.bar2", 99)

    with TestCase.assertRaises(config, RuntimeError):
        config.set("foo_keyed", 99)

    with TestCase.assertRaises(config, RuntimeError):
        config.write_file()
