from unittest.mock import patch
from pyxavi.config import Config
from pyxavi.logger import Logger
import logging

CONFIG = {
    "logger.format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
    "logger.filename": "test.log",
    "logger.to_file": False,
    "logger.to_stdout": True,
    "logger.loglevel": 45,
    "logger.name": "logger_test"
}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default) -> str:
    return CONFIG[param] if param in CONFIG else default


@patch("pyxavi.config.Config.__init__", new=patched_config_init)
@patch("pyxavi.config.Config.get", new=patched_config_get)
def test_initialize_logger():

    config = Config()

    new_instance = Logger(config).get_logger()

    from_logging = logging.getLogger(CONFIG["logger.name"])

    assert new_instance == from_logging
