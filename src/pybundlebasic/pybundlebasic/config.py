from .storage import Storage
import os

CONFIG_FILENAME = "config.yaml"


class Config(Storage):
    """Class to handle a config file

    It inherits from the Storage class but denying all
    writes. It is a read-only class.

    :Authors:
        Xavier Arnaus <xavi@arnaus.net>

    """

    def __init__(self, filename: str = CONFIG_FILENAME) -> None:
        super().__init__(filename=filename)

    def read_file(self) -> None:
        if os.path.exists(self._filename):
            super()._load_file_contents()
        else:
            raise RuntimeError("Config file not found")

    def write_file(self) -> None:
        raise RuntimeError("Config class does not allow writting")

    def set(self, param_name: str, value: any = None, dictionary=None):
        raise RuntimeError("Config class does not allow writting")

    def set_hashed(self, param_name: str, value: any = None):
        raise RuntimeError("Config class does not allow writting")
