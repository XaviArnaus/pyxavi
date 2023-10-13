from .config import Config
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

    def __init__(self, config: Config, base_path: str = None) -> None:
        log_format = (
            config.get(
                "logger.format", "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
            )
        )

        handlers = []
        if config.get("logger.to_file", False):
            filename = config.get("logger.filename", 'debug.log')
            if base_path is not None:
                filename = os.path.join(base_path, filename)
            handlers.append(logging.FileHandler(filename, mode='a'))
        if config.get("logger.to_stdout", False):
            handlers.append(logging.StreamHandler(sys.stdout))

        # Define basic configuration
        logging.basicConfig(
            # Define logging level
            level=config.get("logger.loglevel", 20),
            # Define the format of log messages
            format=log_format,
            # Declare handlers
            handlers=handlers
        )
        # Define your own logger name
        self._logger = logging.getLogger(config.get("logger.name", "custom_logger"))

    def get_logger(self) -> logging:
        return self._logger
