from unittest.mock import patch
from pyxavi.config import Config
from pyxavi.logger import Logger
import logging

CONFIG = {
    "logger": {
        "format": "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s",
        "filename": "test.log",
        "to_file": False,
        "to_stdout": True,
        "loglevel": 45,
        "name": "logger_test"
    }
}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default) -> str:
    return CONFIG[param] if param in CONFIG else default

def patch_config_read_file(self):
    self._content = CONFIG


@patch.object(Config, "read_file", new=patch_config_read_file)
def test_initialize_logger():

    config = Config()

    new_instance = Logger(config).get_logger()

    from_logging = logging.getLogger(CONFIG["logger"]["name"])

    assert new_instance == from_logging
