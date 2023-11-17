from unittest.mock import patch, Mock
from pyxavi.config import Config
from pyxavi.logger import Logger
from logging.handlers import TimedRotatingFileHandler
from datetime import time
from logging import Logger as OriginalLogger
import logging
import copy
import pytest

CONFIG = {
    "logger": {
        "format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
        "filename": "test.log",
        "to_file": False,
        "to_stdout": True,
        "loglevel": 45,
        "name": "logger_test",
        "rotate_files": False,
        "when_rotate": "midnight",
        "backup_count": 10,
        "encoding": "UTF-8",
        "utc": False,
        "at_time": (1,0,0)
    }
}

_logger: OriginalLogger = None
_orig_handlers: list = []
_orig_level: int = None

@pytest.fixture(autouse=True)
def setup_function():

    global CONFIG

    backup = copy.deepcopy(CONFIG)

    # global _logger
    # global _orig_handlers
    # global _orig_level

    # _logger = logging.getLogger(CONFIG["logger"]["name"])
    # _orig_handlers = _logger.handlers
    # _logger.handlers = []
    # _orig_level = _logger.level

    yield

    # _logger.handlers = _orig_handlers
    # _logger.level = _orig_level

    CONFIG = backup


def patch_config_read_file(self):
    self._content = CONFIG

def patch_logging_getLogger(name):
    pass


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

    CONFIG["logger"]["to_stdout"] = True
    CONFIG["logger"]["to_file"] = False
    config = Config()

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)



@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_only_file_default_no_rotate():

    CONFIG["logger"]["to_stdout"] = False
    CONFIG["logger"]["to_file"] = True
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
        filename=CONFIG["logger"]["filename"],
        mode="a",
        encoding=CONFIG["logger"]["encoding"]
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_both_stdout_and_file_default_no_rotate():

    CONFIG["logger"]["to_stdout"] = True
    CONFIG["logger"]["to_file"] = True
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
        filename=CONFIG["logger"]["filename"],
        mode="a",
        encoding=CONFIG["logger"]["encoding"]
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_file_default_with_rotate():

    CONFIG["logger"]["to_stdout"] = False
    CONFIG["logger"]["to_file"] = True
    CONFIG["logger"]["rotate_files"] = True
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
        filename=CONFIG["logger"]["filename"],
        when=CONFIG["logger"]["when_rotate"],
        backupCount=CONFIG["logger"]["backup_count"],
        encoding=CONFIG["logger"]["encoding"],
        utc=False,
        atTime=time(*CONFIG["logger"]["at_time"]),
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_file_default_with_rotate_UTC():

    CONFIG["logger"]["to_stdout"] = False
    CONFIG["logger"]["to_file"] = True
    CONFIG["logger"]["rotate_files"] = True
    CONFIG["logger"]["utc"] = True
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
        filename=CONFIG["logger"]["filename"],
        when=CONFIG["logger"]["when_rotate"],
        backupCount=CONFIG["logger"]["backup_count"],
        encoding=CONFIG["logger"]["encoding"],
        utc=True,
        atTime=time(*CONFIG["logger"]["at_time"]),
    )


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_logger_file_default_with_rotate_every_hour():

    CONFIG["logger"]["to_stdout"] = False
    CONFIG["logger"]["to_file"] = True
    CONFIG["logger"]["rotate_files"] = True
    CONFIG["logger"]["when_rotate"] = "H"
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
        filename=CONFIG["logger"]["filename"],
        when="H",
        backupCount=CONFIG["logger"]["backup_count"],
        encoding=CONFIG["logger"]["encoding"],
        utc=False,
        atTime=time(*CONFIG["logger"]["at_time"]),
    )