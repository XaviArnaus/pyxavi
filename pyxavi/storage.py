from hashlib import sha256
from pathlib import Path
import yaml
import os


class Storage:
    """Class to handle file-based simple storage

    Basic load/write, get/set behaviour for key/value
    file-based storage.

    :Authors:
        Xavier Arnaus <xavi@arnaus.net>

    """

    def __init__(self, filename) -> None:
        self._filename = filename
        self._content = {}
        self.read_file()

    @staticmethod
    def _load_file_contents(filename: str) -> dict:
        with open(filename, 'r') as stream:
            return yaml.safe_load(stream)

    def read_file(self) -> None:
        if os.path.exists(self._filename):
            self._content = self._load_file_contents(self._filename)
        else:
            Path(self._filename).touch()

    def write_file(self) -> None:
        with open(self._filename, 'w+') as stream:
            yaml.safe_dump(self._content, stream)

    def get(self, param_name: str = "", default_value: any = None) -> any:
        if param_name.find(".") > 0:
            local_content = self._content
            for item in param_name.split("."):
                if item in local_content and local_content[item]:
                    local_content = local_content[item]
                else:
                    return default_value
            return local_content

        return self._content[param_name] \
            if self._content and param_name in self._content \
            else default_value

    def get_all(self) -> dict:
        return self._content

    def set(self, param_name: str, value: any = None, dictionary=None):
        if param_name is None:
            raise RuntimeError("Params must have a name")

        if param_name.find(".") > 0:
            pieces = param_name.split(".")
            if (dictionary is None and pieces[0] not in self._content) or \
                    (dictionary is not None and pieces[0] not in dictionary):
                raise RuntimeError(
                    "Storage path [{}] unknown in [{}]".format(
                        param_name, dictionary if dictionary else self._content
                    )
                )

            self.set(
                ".".join(pieces[1:]),
                value,
                self._content[pieces[0]] if not dictionary else dictionary[pieces[0]]
            )
        else:
            if dictionary is not None:
                dictionary[param_name] = value
            elif self._content is not None:
                self._content[param_name] = value
            else:
                self._content = {param_name: value}

    def get_hashed(self, param_name: str = "", default_value: any = None) -> any:
        # if param_name.find(".") > 0:
        #     last = param_name[-1]
        #     param_name = param_name[0:-1]
        #     param_name = param_name + sha256(last.encode()).hexdigest()
        # else:
        param_name = sha256(param_name.encode()).hexdigest()

        return self.get(param_name, default_value)

    def set_hashed(self, param_name: str, value: any = None):
        # if param_name.find(".") > 0:
        #     last = param_name[-1]
        #     param_name = param_name[0:-1]
        #     param_name = param_name + sha256(last.encode()).hexdigest()
        # else:
        param_name = sha256(param_name.encode()).hexdigest()

        self.set(param_name, value)
