from .config import Config
from logging.handlers import TimedRotatingFileHandler
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
        "utc": False
    }
    DEFAULT_STDOUT_LOGGING = {
        "active": False
    }
    DEFAULT_LOG_LEVEL = 20

    def __init__(self, config: Config, base_path: str = None) -> None:
        # Common parameters
        log_format = config.get("logger.format", self.DEFAULT_LOG_FORMAT)
        log_level = config.get("logger.loglevel", self.DEFAULT_LOG_LEVEL)
        # File logging
        file_logging_wanted = config.get("logger.to_file", self.DEFAULT_FILE_LOGGING["active"])
        filename = config.get("logger.filename", self.DEFAULT_FILE_LOGGING["filename"])
        if base_path is not None:
            filename = os.path.join(base_path, filename)
        rotate_is_wanted = config.get("logger.rotate_files", self.DEFAULT_FILE_LOGGING["rotate_files"])
        when_to_rotate = config.get("logger.when_rotate", self.DEFAULT_FILE_LOGGING["when_rotate"])
        backup_count = config.get("logger.backup_count", self.DEFAULT_FILE_LOGGING["backup_count"])
        encoding = config.get("logger.encoding", self.DEFAULT_FILE_LOGGING["encoding"])
        utc = config.get("logger.utc", self.DEFAULT_FILE_LOGGING["utc"])
        # Standard output logging
        stdout_logging_wanted = config.get("logger.to_stdout", self.DEFAULT_STDOUT_LOGGING["active"])

        handlers = []
        if file_logging_wanted:
            if rotate_is_wanted:
                handlers.append(
                    TimedRotatingFileHandler(
                        filename=filename, 
                        when=when_to_rotate,
                        backupCount=backup_count,
                        encoding=encoding,
                        utc=utc
                    )
                )
            else:
                handlers.append(logging.FileHandler(filename=filename, mode='a', encoding=encoding))
            
        if stdout_logging_wanted:
            handlers.append(logging.StreamHandler(sys.stdout))

        # Define basic configuration
        logging.basicConfig(
            # Define logging level
            level=log_level,
            # Define the format of log messages
            format=log_format,
            # Declare handlers
            handlers=handlers
        )
        # Define your own logger name
        self._logger = logging.getLogger(config.get("logger.name", "custom_logger"))
    


    def get_logger(self) -> logging:
        return self._logger
