from unittest.mock import patch, Mock
from pyxavi import Config, Logger, PIDFileHandler, PIDTimedRotateFileHandler, Dictionary
from pyxavi.logger import ColorFormatter
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, time
import logging
import copy
import os
import tempfile
import pytest
import yaml
import multiprocessing_logging

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
            "multiprocess": False,
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
            "active": True, "multiprocess": False
        }
    }
}


@pytest.fixture(autouse=True)
def setup_function():

    global CONFIG

    backup = copy.deepcopy(CONFIG)

    yield

    CONFIG = backup


def test_initialize_logger_old_config():

    config = Config(params=CONFIG_OLD)

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


def test_logger_old_only_stdout():

    CONFIG_OLD["logger"]["to_stdout"] = True
    CONFIG_OLD["logger"]["to_file"] = False
    config = Config(params=CONFIG_OLD)

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)


def test_logger_old_only_file_default_no_rotate():

    CONFIG_OLD["logger"]["to_stdout"] = False
    CONFIG_OLD["logger"]["to_file"] = True
    config = Config(params=CONFIG_OLD)

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


def test_logger_old_both_stdout_and_file_default_no_rotate():

    CONFIG_OLD["logger"]["to_stdout"] = True
    CONFIG_OLD["logger"]["to_file"] = True
    config = Config(params=CONFIG_OLD)

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


def test_initialize_logger():

    config = Config(params=CONFIG)

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


def test_logger_only_stdout():

    CONFIG["logger"]["stdout"]["active"] = True
    CONFIG["logger"]["file"]["active"] = False
    config = Config(params=CONFIG)

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], logging.StreamHandler)


def test_logger_only_file_default_no_rotate():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    config = Config(params=CONFIG)

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


def test_logger_both_stdout_and_file_default_no_rotate():

    CONFIG["logger"]["stdout"]["active"] = True
    CONFIG["logger"]["file"]["active"] = True
    config = Config(params=CONFIG)

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


def test_logger_both_stdout_and_file_default_no_rotate_with_multiprocess(monkeypatch):

    CONFIG["logger"]["stdout"]["active"] = True
    CONFIG["logger"]["stdout"]["multiprocess"] = True
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["multiprocess"] = True
    config = Config(params=CONFIG)

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = PIDFileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    mock_install_mp_handler = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(PIDFileHandler, "__init__", new=mock_file_handler_init):
            with patch.object(multiprocessing_logging,
                              "install_mp_handler",
                              new=mock_install_mp_handler):
                _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 2
    assert isinstance(call_arguments["handlers"][0], PIDFileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        mode="a",
        encoding=CONFIG["logger"]["file"]["encoding"]
    )
    mock_install_mp_handler.assert_called_once()


def test_logger_file_default_with_rotate():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    config = Config(params=CONFIG)

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
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"],
                                 "%H:%M:%S").time(),
    )


def test_logger_file_default_with_rotate_and_multiprocess():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["multiprocess"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    config = Config(params=CONFIG)

    mock_logging_basic_config = Mock()
    mock_file_handler = Mock()
    mock_file_handler.__class__ = PIDTimedRotateFileHandler
    mock_file_handler_init = Mock()
    mock_file_handler_init.return_value = None
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        with patch.object(PIDTimedRotateFileHandler, "__init__", new=mock_file_handler_init):
            _ = Logger(config)

    call_arguments = mock_logging_basic_config.mock_calls[0][2]
    assert len(call_arguments["handlers"]) == 1
    assert isinstance(call_arguments["handlers"][0], PIDTimedRotateFileHandler)
    mock_file_handler_init.assert_called_once_with(
        filename=CONFIG["logger"]["file"]["filename"],
        when=CONFIG["logger"]["file"]["rotate"]["when"],
        backupCount=CONFIG["logger"]["file"]["rotate"]["backup_count"],
        encoding=CONFIG["logger"]["file"]["encoding"],
        utc=False,
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"],
                                 "%H:%M:%S").time(),
    )


def test_logger_file_default_with_rotate_UTC():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["utc"] = True
    config = Config(params=CONFIG)

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
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"],
                                 "%H:%M:%S").time(),
    )


def test_logger_file_default_with_rotate_every_hour():

    CONFIG["logger"]["stdout"]["active"] = False
    CONFIG["logger"]["file"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["active"] = True
    CONFIG["logger"]["file"]["rotate"]["when"] = "H"
    config = Config(params=CONFIG)

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
        atTime=datetime.strptime(CONFIG["logger"]["file"]["rotate"]["at_time"],
                                 "%H:%M:%S").time(),
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

    config = Config(filename="faked.yaml")

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


def test_loading_old_config_prints_deprecation_warning(caplog):

    CONFIG_OLD["logger"]["to_stdout"] = True
    CONFIG_OLD["logger"]["to_file"] = False
    config = Config(params=CONFIG_OLD)

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    expected_warning = "[pyxavi] An old version of the configuration " +\
        "file structure for the Logger module has been loaded. This is " +\
        "deprecated.\n" +\
        "Please migrate your configuration file to the new structure.\n" +\
        "Read https://github.com/XaviArnaus/pyxavi/blob/main/docs/logger.md"

    assert expected_warning in caplog.text


def test_loading_config_does_not_prints_deprecation_warning(caplog):

    CONFIG["logger"]["stdout"]["active"] = True
    CONFIG["logger"]["file"]["active"] = False
    config = Config(params=CONFIG)

    mock_logging_basic_config = Mock()
    with patch.object(logging, "basicConfig", new=mock_logging_basic_config):
        _ = Logger(config)

    expected_warning = "[pyxavi] An old version of the configuration " +\
        "file structure for the Logger module has been loaded. This is " +\
        "deprecated.\n" +\
        "Please migrate your configuration file to the new structure.\n" +\
        "Read https://github.com/XaviArnaus/pyxavi/blob/main/docs/logger.md"

    assert expected_warning not in caplog.text


# --- ColorFormatter fallbacks and the PID handlers ---


def _record(name="n", level=logging.INFO, process="MainProcess", thread="MainThread"):
    record = logging.LogRecord(name, level, __file__, 1, "the message", None, None)
    record.processName = process
    record.threadName = thread
    return record


def _formatter(profile: str) -> ColorFormatter:
    config = Dictionary(
        {
            "format": "[%(levelname)s] %(processName)s %(threadName)s %(message)s",
            "stdout": {
                "colorize": {
                    "profile": profile,
                    "only_the_field": False,
                    "by_process": {
                        "MainProcess": "GREEN"
                    },
                    "by_thread": {
                        "MainThread": "GREEN"
                    },
                    "support": {
                        "UNKNOWN": "BOLD"
                    },
                    "colors": {
                        "GREEN": "<g>",
                        "BOLD": "<b>",
                        "END": "<e>",
                        "WHITE": "<w>",
                        "BLUE": "<bl>",
                        "ORANGE": "<o>",
                        "RED": "<r>",
                        "RED_BRIGHT": "<rb>"
                    }
                }
            }
        }
    )
    return ColorFormatter(config)


@pytest.mark.parametrize(
    argnames=("profile", "kwargs", "expected_color"),
    argvalues=[
        ("by_process", {
            "process": "MainProcess"
        }, "<g>"),
        ("by_process", {
            "process": "SomethingElse"
        }, "<b>"),
        ("by_thread", {
            "thread": "MainThread"
        }, "<g>"),
        ("by_thread", {
            "thread": "Thread-7"
        }, "<b>"),
        ("by_level", {
            "level": logging.INFO
        }, "<bl>"),
        ("by_level", {
            "level": 45
        }, "<b>"),
    ],
)
def test_color_formatter_unknown_names_and_levels_keep_the_full_line(
    profile, kwargs, expected_color
):
    output = _formatter(profile).format(_record(**kwargs))

    # The whole line is kept (not just the message), coloured with the expected color
    assert output.startswith(expected_color + "[")
    assert output.endswith("the message<e>")
    assert "] " in output


def test_color_formatter_without_config_formats_the_plain_line():
    output = ColorFormatter().format(_record())

    assert "INFO" in output
    assert output.endswith("the message")


def test_color_formatter_instances_do_not_share_formats():
    first = _formatter("by_process")
    second = _formatter("by_thread")

    assert "MainProcess" in first.FORMATS
    assert "MainProcess" not in second.FORMATS
    assert "MainProcess" not in ColorFormatter.FORMATS


def test_color_formatter_does_not_alter_the_given_colors():
    colors = {"X": "\\033[1m", "END": "e"}
    config = Dictionary({"stdout": {"colorize": {"colors": colors}}})

    decoded = ColorFormatter().load_colors_from_config(config)

    assert decoded["X"] == "\033[1m"
    assert colors["X"] == "\\033[1m"


def test_pid_file_handler_passes_the_delay_and_errors():
    with tempfile.TemporaryDirectory() as folder:
        handler = PIDFileHandler(os.path.join(folder, "a.log"), delay=True, errors="replace")
        try:
            assert handler.stream is None
            assert handler.errors == "replace"
            assert str(os.getpid()) in handler.baseFilename
        finally:
            handler.close()


def test_pid_timed_rotate_handler_passes_interval_delay_and_errors():
    with tempfile.TemporaryDirectory() as folder:
        handler = PIDTimedRotateFileHandler(
            os.path.join(folder, "a.log"), when="S", interval=5, delay=True, errors="replace"
        )
        try:
            assert handler.interval == 5
            assert handler.stream is None
            assert handler.errors == "replace"
            assert str(os.getpid()) in handler.baseFilename
        finally:
            handler.close()


def test_loggers_do_not_share_the_list_of_handlers():
    first = Logger(Config(params={"logger": {"stdout": {"active": True}}}))
    second = Logger(Config(params={"logger": {"stdout": {"active": True}}}))

    assert first._handlers is not second._handlers
    assert Logger._handlers == []
