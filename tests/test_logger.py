from unittest.mock import patch, Mock
from pyxavi.config import Config
from pyxavi.logger import Logger
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, time
import logging
import copy
import pytest
import yaml

CONFIG_OLD = {
    "logger": {
        "format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
        "filename": "test.log",
        "to_file": False,
        "to_stdout": True,
        "loglevel": 45,
        "name": "logger_test"
    }
}

CONFIG = {
    "logger": {
        "format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
        "loglevel": 45,
        "name": "logger_test",
        "file": {
            "active": False,
            "filename": "test.log",
            "encoding": "UTF-8",
            "rotate": {
                "active": False,
                "when": "midnight",
                "backup_count": 10,
                "utc": False,
                "at_time": "1:0:0"
            }
        },
        "stdout": {
            "active": True
        }
    }
}


@pytest.fixture(autouse=True)
def setup_function():

    global CONFIG

    backup = copy.deepcopy(CONFIG)

    yield

    CONFIG = backup


def patch_config_read_file(self):
    self._content = CONFIG


def patch_config_old_read_file(self):
    self._content = CONFIG_OLD


@patch.object(Config, "read_file", new=patch_config_old_read_file)
def test_initialize_logger_old_config():

    config = Config()

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    # Asserts are related to the content received from the file,
    #   here they are mocked to what comes from the dict above
    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert call_arguments["level"] == CONFIG_OLD["logger"]["loglevel"]
    assert call_arguments["format"] == CONFIG_OLD["logger"]["format"]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)


@patch.object(Config, "read_file", new=patch_config_old_read_file)
def test_logger_old_only_stdout():

    CONFIG_OLD["logger"]["to_stdout"] = True
    CONFIG_OLD["logger"]["to_file"] = False
    config = Config()

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)


@patch.object(Config, "read_file", new=patch_config_old_read_file)
def test_logger_old_only_file_default_no_rotate():

    CONFIG_OLD["logger"]["to_stdout"] = False
    CONFIG_OLD["logger"]["to_file"] = True
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = logging.FileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(logging.FileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.FileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG_OLD["logger"]["filename"], mode="a", encoding="UTF-8"
    )


@patch.object(Config, "read_file", new=patch_config_old_read_file)
def test_logger_old_both_stdout_and_file_default_no_rotate():

    CONFIG_OLD["logger"]["to_stdout"] = True
    CONFIG_OLD["logger"]["to_file"] = True
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = logging.FileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(logging.FileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 2
    assert isinstance(call_arguments["handlers"][0], logging.FileHandler)
    assert isinstance(call_arguments["handlers"][1], logging.StreamHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG_OLD["logger"]["filename"], mode="a", encoding="UTF-8"
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_initialize_logger():

    config = Config()

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    # Asserts are related to the content received from the file,
    #   here they are mocked to what comes from the dict above
    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert call_arguments["level"] == CONFIG["logger"]["loglevel"]
    assert call_arguments["format"] == CONFIG["logger"]["format"]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_only_stdout():

    CONFIG["logger"]["stdout"]["active"] = True
    CONFIG["logger"]["file"]["active"] = False
    config = Config()

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_only_file_default_no_rotate():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = logging.FileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(logging.FileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.FileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        mode="a",
        encoding=CONFIG["logger"]["file"]["encoding"]
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_both_stdout_and_file_default_no_rotate():

    CONFIG["logger"]["stdout"]["active"] = True
    CONFIG["logger"]["file"]["active"] = True
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = logging.FileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(logging.FileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 2
    assert isinstance(call_arguments["handlers"][0], logging.FileHandler)
    assert isinstance(call_arguments["handlers"][1], logging.StreamHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        mode="a",
        encoding=CONFIG["logger"]["file"]["encoding"]
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_file_default_with_rotate():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = TimedRotatingFileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(TimedRotatingFileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], TimedRotatingFileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        when=CONFIG["logger"]["file"]["rotate"]["when"],
        backupCount=CONFIG["logger"]["file"]["rotate"]["backup_count"],
        encoding=CONFIG["logger"]["file"]["encoding"],
        utc=False,
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"], "%H:%M:%S").time(),
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_file_default_with_rotate_UTC():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["utc"] = True
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = TimedRotatingFileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(TimedRotatingFileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], TimedRotatingFileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        when=CONFIG["logger"]["file"]["rotate"]["when"],
        backupCount=CONFIG["logger"]["file"]["rotate"]["backup_count"],
        encoding=CONFIG["logger"]["file"]["encoding"],
        utc=True,
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"], "%H:%M:%S").time(),
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_file_default_with_rotate_every_hour():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["when"] = "H"
    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = TimedRotatingFileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(TimedRotatingFileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], TimedRotatingFileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        when="H",
        backupCount=CONFIG["logger"]["file"]["rotate"]["backup_count"],
        encoding=CONFIG["logger"]["file"]["encoding"],
        utc=False,
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"], "%H:%M:%S").time(),
    )

def patch_config_read_file_yaml(self):
    content = """
# Logging config
logger:
  # [Integer] Log level: NOTSET=0 | DEBUG=10 | INFO=20 | WARN=30 | ERROR=40 | CRITICAL=50
  loglevel: 30
  # [String] Name of the logger
  name: "my_app"
  # [String] Format of the log
  format: "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
  # File related parameters
  file:
    # [Bool] Dump the log into a file
    active: True
    # [String] Path and filename of the log file
    filename: "log/my_app.log"
    # [String] The encoding of the log file
    encoding: "UTF-8"
    # [Bool] Do we want to rotate the log files? Only will apply if we log to files
    rotate:
        active: True
        # [String] When do we rotate. Accepts "S" | "M" | "H" | "D" | "W0"-"W6" | "midnight"
        #   See https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
        when: "S"
        # [Int] How many rotated old files to keep before it starts to delete the older
        backup_count: 20
        # [Bool] Stick to UTC timings when triggering the rotation
        utc: True
        # [String] in format "%H:%M:%S". When to trigger THE VERY FIRST rotation.
        #   Subsequent will attend to when_rotate
        at_time: "2:00:00"
  # Standard output related parameters
  stdout:
  # [Bool] Dump the log into a stdout
      active: False
"""
    self._content = yaml.safe_load(content)

@patch.object(Config, "read_file", new=patch_config_read_file_yaml)
def test_from_yaml_config():

    config = Config()

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = TimedRotatingFileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(TimedRotatingFileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], TimedRotatingFileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename="log/my_app.log",
        when="S",
        backupCount=20,
        encoding=CONFIG["logger"]["file"]["encoding"],
        utc=True,
        atTime=time(2, 0, 0)
    )
