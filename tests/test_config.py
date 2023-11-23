from unittest.mock import Mock, patch, call, mock_open
from pyxavi.config import Config
from pyxavi.storage import Storage
from unittest import TestCase
import os

CONFIG = {"foo": {"bar": "hola", "foo2": {"bar2": "adios"}}, "que": "tal"}


def patched_yaml_safe_load(stream):
    return CONFIG


def os_path_exists_true(path):
    return True


def os_path_exists_false(path):
    return False


def initialize():
    return Config(params=CONFIG)


def test_initialize_config_with_params():
    config = initialize()

    assert config._content == CONFIG


def test_initialize_config_without_params_exception():
    with TestCase.assertRaises("pyxavi.config", RuntimeError):
        _ = Config()


@patch("yaml.safe_load", new=patched_yaml_safe_load)
@patch("builtins.open", mock_open(read_data=""))
@patch("os.path.exists", new=os_path_exists_true)
def test_initialize_config_with_filename():
    filename = "another_file.yaml"
    config = Config(filename=filename)

    assert config._filename == filename
    assert config._content == CONFIG


@patch("os.path.exists", new=os_path_exists_false)
def test_initialize_config_file_not_found_exception():
    with TestCase.assertRaises("pyxavi.config", RuntimeError):
        _ = Config(filename="not_existing.yaml")


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


@patch("os.path.exists", new=os_path_exists_true)
def test_merging_from_file_path_exists():
    first_file_name = "first.yaml"
    first_file_content = CONFIG
    second_file_name = "second.yaml"
    second_file_content = {"molt": "be"}

    mocked_load_file_contents = Mock()
    mocked_load_file_contents.side_effect = [first_file_content, second_file_content]
    with patch.object(Storage, "_load_file_contents", new=mocked_load_file_contents):
        config = Config(filename=first_file_name)
        config.merge_from_file(filename=second_file_name)

    mocked_load_file_contents.assert_has_calls([call(first_file_name), call(second_file_name)])

    assert config.get("que") == "tal"
    assert config.get("molt") == "be"


@patch("os.path.exists", new=os_path_exists_true)
def test_merging_from_file_path_exists_and_overwrites():
    first_file_name = "first.yaml"
    first_file_content = CONFIG
    second_file_name = "second.yaml"
    second_file_content = {"que": "passa"}

    mocked_load_file_contents = Mock()
    mocked_load_file_contents.side_effect = [first_file_content, second_file_content]
    with patch.object(Storage, "_load_file_contents", new=mocked_load_file_contents):
        config = Config(filename=first_file_name)
        config.merge_from_file(filename=second_file_name)

    mocked_load_file_contents.assert_has_calls([call(first_file_name), call(second_file_name)])

    assert config.get("que") == "passa"


def test_merging_from_file_path_not_exists():
    first_file_name = "first.yaml"
    first_file_content = CONFIG

    mocked_load_file_contents = Mock()
    mocked_load_file_contents.return_value = first_file_content
    mocked_path_exists = Mock()
    mocked_path_exists.side_effect = [True, False]
    with patch.object(os.path, "exists", new=mocked_path_exists):
        with patch.object(Storage, "_load_file_contents", new=mocked_load_file_contents):
            config = Config(filename=first_file_name)

        with TestCase.assertRaises(config, RuntimeError):
            config.merge_from_file(filename="second.yaml")
