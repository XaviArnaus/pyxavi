from pyxavi.config import Config
from pyxavi.dictionary import Dictionary
from logging.handlers import TimedRotatingFileHandler
from datetime import time
from logging import Logger as OriginalLogger
import logging
import sys
import os


class Logger:
    """Class to help on instantiating Logging

    It uses the built-in logging infra, but takes the
    configuration from the given config object.

    It is meant to be used the first time in the initial
    executor, then passed through the code.

    The built-in logging system can also be used to pick up
    an already instantiated logger with this class,
    making it very versatile.

    :Authors:
        Xavier Arnaus <xavi@arnaus.net>

    """

    DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
    DEFAULT_FILE_LOGGING = {
        "active": False,
        "filename": "debug.log",
        "rotate_files": False,
        # "S" | "M" | "H" | "D" | "W0"-"W6" | "midnight"
        "when_rotate": "midnight",
        # How many old rotated log files to keep
        "backup_count": 10,
        "encoding": "UTF-8",
        "utc": False,
        # Hour, Minute, Second
        "at_time": (1,0,0)
    }
    DEFAULT_STDOUT_LOGGING = {"active": False}
    DEFAULT_LOG_LEVEL = 20
    DEFAULT_LOGGER_NAME = "custom_logger"

    _logger: OriginalLogger = None
    _base_path: str = None
    _logger_config: Dictionary = None
    _handlers = []

    def __init__(self, config: Config, base_path: str = None) -> None:

        self._base_path = base_path
        self._load_config(config=config)

        # Setting up the handlers straight away
        self._clean_handlers()
        self._set_handlers()

        # Define basic configuration
        logging.basicConfig(
            # Define logging level
            level=self._logger_config.get("loglevel"),
            # Define the format of log messages
            format=self._logger_config.get("format"),
            # Declare handlers
            handlers=self._handlers
        )
        # Define your own logger name
        self._logger = logging.getLogger(self._logger_config.get("name"))
    
    def _load_config(self, config: Config) -> None:
        # Previous work
        filename = config.get("logger.filename", self.DEFAULT_FILE_LOGGING["filename"])
        if self._base_path is not None:
            filename = os.path.join(self._base_path, filename)

        # What we do here is to build a main dict where we ensure we always have a value.
        self._logger_config = Dictionary({
            # Common parameters
            "name": config.get("logger.name", self.DEFAULT_LOGGER_NAME),
            "loglevel": config.get("logger.loglevel", self.DEFAULT_LOG_LEVEL),
            "format": config.get("logger.format", self.DEFAULT_LOG_FORMAT),
            # File logging
            "file": {
                "active": config.get("logger.to_file", self.DEFAULT_FILE_LOGGING["active"]),
                "filename": filename,
                "encoding": config.get("logger.encoding", self.DEFAULT_FILE_LOGGING["encoding"]),
                "rotate": {
                    "active": config.get("logger.rotate_files", self.DEFAULT_FILE_LOGGING["rotate_files"]),
                    "when": config.get("logger.when_rotate", self.DEFAULT_FILE_LOGGING["when_rotate"]),
                    "backup_count": config.get("logger.backup_count", self.DEFAULT_FILE_LOGGING["backup_count"]),
                    "utc": config.get("logger.utc", self.DEFAULT_FILE_LOGGING["utc"]),
                    "at_time": time(*config.get("logger.at_time", self.DEFAULT_FILE_LOGGING["at_time"]))
                },
            },
            # Standard output logging
            "stdout": {
                "active": config.get("logger.to_stdout", self.DEFAULT_STDOUT_LOGGING["active"])
            }
        })
    
    def _set_handlers(self) -> None:
        if self._logger_config.get("file.active"):
            if self._logger_config.get("file.rotate.active"):
                self._handlers.append(
                    TimedRotatingFileHandler(
                        filename=self._logger_config.get("file.filename"),
                        when=self._logger_config.get("file.rotate.when"),
                        backupCount=self._logger_config.get("file.rotate.backup_count"),
                        encoding=self._logger_config.get("file.encoding"),
                        utc=self._logger_config.get("file.rotate.utc"),
                        atTime=self._logger_config.get("file.rotate.at_time"),
                    )
                )
            else:
                self._handlers.append(
                    logging.FileHandler(
                        filename=self._logger_config.get("file.filename"),
                        mode='a',
                        encoding=self._logger_config.get("file.encoding")
                    )
                )

        if self._logger_config.get("stdout.active"):
            self._handlers.append(logging.StreamHandler(sys.stdout))
    

    def _clean_handlers(self) -> None:
        if self._logger is not None and self._logger.hasHandlers():
            self._logger.handlers.clear()
        if len(self._handlers) > 0:
            self._handlers = []
        

    def get_logger(self) -> OriginalLogger:
        return self._logger
