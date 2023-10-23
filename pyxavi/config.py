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
            self._content = super()._load_file_contents(self._filename)
        else:
            raise RuntimeError(f"Config file [{self._filename}] not found")

    def merge_from_dict(self, parameters: dict) -> None:
        self._content = {**self._content, **parameters}

    def merge_from_file(self, filename: str) -> None:
        if os.path.exists(filename):
            self.merge_from_dict(parameters=super()._load_file_contents(filename))
        else:
            raise RuntimeError(f"Config file [{filename}] not found")

    def write_file(self) -> None:
        raise RuntimeError("Config class does not allow writting")

    def set(self, param_name: str, value: any = None, dictionary=None):
        raise RuntimeError("Config class does not allow writting")

    def set_hashed(self, param_name: str, value: any = None):
        raise RuntimeError("Config class does not allow writting")
